"""
NormalizationService — Capa 1.5: Normalización Documental, Entidades y Tiempo
TS_015_002_NORMALIZATION_SERVICE_MINIMO
TS_015_004_COLUMN_MAPPING_CATALOG

Servicio mínimo determinístico que procesa un documento crudo (dict) y produce
un NormalizedEvidencePackage.

Reglas:
- Sin IA ni modelos de lenguaje.
- Sin OperationalCase.
- Sin diagnóstico.
- Sin fórmulas de negocio.
- Detección de columnas por catálogo externo JSON (con fallback interno).
- TemporalWindow desde columna fecha si existe; alerta si no.
- No inventa entidades ni datos faltantes.
- Toda variable tiene EvidenceReference trazable.

Catálogo de columnas:
  app/catalogs/column_mapping_catalog.json
  Si el archivo no existe o está corrupto, se usa el fallback interno.

Formato de entrada esperado (dict):
{
    "cliente_id": "...",
    "document_id": "...",          # usado como raw_document_id
    "source_type": "excel",        # FileType
    "columns": ["fecha", "producto", "cant.", "precio", "prov."],
    "rows": [                      # lista de dicts con los valores de cada fila
        {"fecha": "2026-05-01", "producto": "PJ-AZ-42", "cant.": "120", "precio": "5500"},
        ...
    ]
}

Documento rector:
  docs/product/SMARTPYME_CAPA_015_NORMALIZACION_DOCUMENTAL_ENTIDADES_TIEMPO.md
"""

from __future__ import annotations

import json
import uuid
from datetime import date, datetime
from pathlib import Path
from typing import Any, Optional

from app.contracts.normalization_contract import (
    CanonicalEntity,
    CleanVariable,
    ColumnCandidate,
    DocumentSchema,
    EntityAlias,
    EntityMention,
    EvidenceReference,
    NormalizationAlert,
    NormalizedEvidencePackage,
    RawDocument,
    SourceFieldMapping,
    TemporalWindow,
)

# ---------------------------------------------------------------------------
# Ruta por defecto del catálogo externo
# ---------------------------------------------------------------------------

_DEFAULT_CATALOG_PATH = Path(__file__).parent.parent / "catalogs" / "column_mapping_catalog.json"

# ---------------------------------------------------------------------------
# Fallback interno mínimo
# ---------------------------------------------------------------------------
# Usado si el catálogo externo no existe o está corrupto.
# Formato: raw_column_lower → (canonical_field, confidence, field_type, is_ambiguous)

_FALLBACK_COLUMN_MAP: dict[str, tuple[str, float, str, bool]] = {
    "cant.":    ("cantidad",        0.95, "number",     False),
    "cantidad": ("cantidad",        0.99, "number",     False),
    "precio":   ("precio_unitario", 0.95, "amount",     False),
    "producto": ("producto",        0.99, "entity_ref", False),
    "prov.":    ("proveedor",       0.78, "entity_ref", False),
    "proveedor":("proveedor",       0.99, "entity_ref", False),
    "fecha":    ("fecha",           0.90, "date",       False),
}

# ---------------------------------------------------------------------------
# Carga del catálogo
# ---------------------------------------------------------------------------


def _load_catalog(
    catalog_path: Optional[Path] = None,
) -> dict[str, tuple[str, float, str, bool]]:
    """
    Carga el catálogo de mapeo de columnas desde un archivo JSON.

    Retorna un dict: raw_column_lower → (canonical_field, confidence, field_type, is_ambiguous).

    Si el archivo no existe, no es JSON válido o tiene estructura incorrecta,
    retorna el fallback interno sin lanzar excepción.
    """
    path = catalog_path or _DEFAULT_CATALOG_PATH

    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return dict(_FALLBACK_COLUMN_MAP)

    result: dict[str, tuple[str, float, str, bool]] = {}

    try:
        for entry in data.get("mappings", []):
            canonical_field: str = entry["canonical_field"]
            field_type: str = entry.get("field_type", "string")
            default_confidence: float = float(entry.get("default_confidence", 0.7))

            for alias in entry.get("aliases", []):
                raw: str = alias["raw"].strip().lower()
                confidence: float = float(alias.get("confidence", default_confidence))
                is_ambiguous: bool = bool(alias.get("ambiguous", False))
                result[raw] = (canonical_field, confidence, field_type, is_ambiguous)
    except (KeyError, TypeError, ValueError):
        # Estructura inesperada → fallback
        return dict(_FALLBACK_COLUMN_MAP)

    return result if result else dict(_FALLBACK_COLUMN_MAP)


def _normalize_col(col: str) -> str:
    """Normaliza el nombre de columna para lookup: strip + lower."""
    return col.strip().lower()


def _try_parse_date(value: str) -> Optional[date]:
    """Intenta parsear una fecha desde string. Retorna None si falla."""
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d", "%d/%m/%y"):
        try:
            return datetime.strptime(value.strip(), fmt).date()
        except (ValueError, AttributeError):
            continue
    return None


def _try_parse_number(value: str) -> Optional[float]:
    """Intenta parsear un número desde string. Retorna None si falla."""
    try:
        cleaned = value.strip().replace(",", ".").replace(" ", "")
        return float(cleaned)
    except (ValueError, AttributeError):
        return None


# ---------------------------------------------------------------------------
# Servicio
# ---------------------------------------------------------------------------


class NormalizationService:
    """
    Servicio de normalización documental mínimo y determinístico.

    Uso por defecto (carga catálogo desde app/catalogs/column_mapping_catalog.json):
        service = NormalizationService()
        result = service.process(raw_document_dict)

    Uso con catálogo custom (para tests o entornos alternativos):
        service = NormalizationService(catalog_path=Path("/ruta/custom.json"))
        # o bien con dict directo:
        service = NormalizationService(column_map={"cant.": ("cantidad", 0.95, "number", False)})
    """

    def __init__(
        self,
        catalog_path: Optional[Path] = None,
        column_map: Optional[dict[str, tuple[str, float, str, bool]]] = None,
    ) -> None:
        """
        Inicializa el servicio con el catálogo de columnas.

        Prioridad:
          1. column_map explícito (para tests o inyección directa).
          2. catalog_path explícito (archivo JSON alternativo).
          3. Catálogo por defecto en app/catalogs/column_mapping_catalog.json.
          4. Fallback interno si el archivo no existe o está corrupto.
        """
        if column_map is not None:
            self._column_map = column_map
        else:
            self._column_map = _load_catalog(catalog_path)

    def process(
        self,
        raw_document: dict[str, Any],
        case_context: Optional[Any] = None,
    ) -> NormalizedEvidencePackage:
        """
        Procesa un documento crudo y produce un NormalizedEvidencePackage.

        Parámetros:
            raw_document: dict con cliente_id, document_id, source_type, columns, rows.
            case_context: InitialCaseAdmission opcional para contexto adicional.

        Retorna:
            NormalizedEvidencePackage con status READY, PARTIAL o BLOCKED.
        """
        package_id = str(uuid.uuid4())
        cliente_id: str = raw_document.get("cliente_id", "unknown")
        document_id: str = raw_document.get("document_id", str(uuid.uuid4()))
        source_type: str = raw_document.get("source_type", "otro")
        columns: list[str] = raw_document.get("columns", [])
        rows: list[dict[str, Any]] = raw_document.get("rows", [])

        # Extraer case_id del contexto si existe
        source_admission_case_id: Optional[str] = None
        if case_context is not None and hasattr(case_context, "case_id"):
            source_admission_case_id = case_context.case_id

        # Validar file_type
        valid_file_types = {"xlsx", "pdf", "csv", "txt", "image", "json", "xml", "whatsapp", "otro"}
        file_type = source_type if source_type in valid_file_types else "otro"

        # --- Paso 1: RawDocument ---
        raw_doc = RawDocument(
            raw_document_id=document_id,
            cliente_id=cliente_id,
            case_id=source_admission_case_id,
            filename=raw_document.get("filename", f"{document_id}.{file_type}"),
            file_type=file_type,  # type: ignore[arg-type]
            received_at=datetime.utcnow(),
            processing_status="IN_PROGRESS",
        )

        schema_id = f"schema_{document_id}"

        # --- Paso 2: Detectar ColumnCandidates y SourceFieldMappings ---
        column_candidates: list[ColumnCandidate] = []
        field_mappings: list[SourceFieldMapping] = []
        alerts: list[NormalizationAlert] = []
        schema_ambiguities: list[str] = []

        # Mapa de canonical_field → raw_column para uso posterior
        canonical_to_raw: dict[str, str] = {}

        for col in columns:
            col_lower = _normalize_col(col)
            col_id = f"col_{document_id}_{col_lower.replace('.', '_').replace(' ', '_')}"

            if col_lower in self._column_map:
                canonical_field, confidence, field_type, is_ambiguous = self._column_map[col_lower]
                status = "AMBIGUOUS" if is_ambiguous else "CANDIDATE"

                candidate = ColumnCandidate(
                    column_candidate_id=col_id,
                    schema_id=schema_id,
                    raw_column=col,
                    possible_meaning=canonical_field,
                    confidence=confidence,
                    requires_confirmation=is_ambiguous or confidence < 0.85,
                    status=status,  # type: ignore[arg-type]
                )
                column_candidates.append(candidate)

                # Guardar primer mapeo por campo canónico
                if canonical_field not in canonical_to_raw:
                    canonical_to_raw[canonical_field] = col

                mapping = SourceFieldMapping(
                    mapping_id=f"map_{document_id}_{col_lower.replace('.', '_').replace(' ', '_')}",
                    schema_id=schema_id,
                    raw_column=col,
                    canonical_field=canonical_field,
                    canonical_field_type=field_type,
                    confidence=confidence,
                    requires_confirmation=is_ambiguous or confidence < 0.85,
                    status="CANDIDATE",
                )
                field_mappings.append(mapping)

                if is_ambiguous:
                    schema_ambiguities.append(
                        f"Columna '{col}' es ambigua: podría ser '{canonical_field}' u otro campo."
                    )
                    alerts.append(NormalizationAlert(
                        alert_id=f"alert_ambig_{col_id}",
                        alert_type="COLUMN_AMBIGUOUS",
                        ambiguity_level="MEDIUM",
                        description=f"Columna '{col}' es ambigua. Requiere confirmación.",
                        affected_object_id=col_id,
                        suggested_action=f"Confirmar si '{col}' representa '{canonical_field}'.",
                    ))
            else:
                # Columna no reconocida en el catálogo
                candidate = ColumnCandidate(
                    column_candidate_id=col_id,
                    schema_id=schema_id,
                    raw_column=col,
                    possible_meaning=None,
                    confidence=0.0,
                    requires_confirmation=True,
                    status="AMBIGUOUS",
                )
                column_candidates.append(candidate)
                schema_ambiguities.append(f"Columna '{col}' no reconocida.")
                alerts.append(NormalizationAlert(
                    alert_id=f"alert_unknown_{col_id}",
                    alert_type="COLUMN_AMBIGUOUS",
                    ambiguity_level="HIGH",
                    description=f"Columna '{col}' no pudo mapearse a ningún campo canónico.",
                    affected_object_id=col_id,
                    suggested_action=f"Indicar qué representa la columna '{col}'.",
                ))

        # --- Paso 3: DocumentSchema ---
        has_product_col = "producto" in canonical_to_raw
        has_fecha_col = "fecha" in canonical_to_raw
        has_cantidad_col = "cantidad" in canonical_to_raw
        has_precio_col = "precio_unitario" in canonical_to_raw
        has_proveedor_col = "proveedor" in canonical_to_raw

        schema_status = "CLEAN" if not schema_ambiguities else "AMBIGUOUS"

        doc_schema = DocumentSchema(
            schema_id=schema_id,
            raw_document_id=document_id,
            detected_columns=column_candidates,
            detected_entity_types=(
                ["producto"] if has_product_col else []
            ) + (
                ["proveedor"] if has_proveedor_col else []
            ),
            row_count=len(rows),
            has_header=True,
            detection_confidence=0.85 if not schema_ambiguities else 0.65,
            ambiguities=schema_ambiguities,
            schema_status=schema_status,  # type: ignore[arg-type]
        )

        # --- Paso 4: TemporalWindow ---
        temporal_window: Optional[TemporalWindow] = None
        tw_id = f"tw_{document_id}"

        if has_fecha_col and rows:
            raw_fecha_col = canonical_to_raw["fecha"]
            dates: list[date] = []
            for row in rows:
                raw_val = str(row.get(raw_fecha_col, "")).strip()
                parsed = _try_parse_date(raw_val)
                if parsed:
                    dates.append(parsed)

            if dates:
                min_date = min(dates)
                max_date = max(dates)
                if min_date == max_date:
                    temporal_window = TemporalWindow(
                        window_id=tw_id,
                        observed_at=min_date,
                        temporal_status="KNOWN",
                        resolution_notes="Fecha única detectada en columna fecha.",
                    )
                else:
                    temporal_window = TemporalWindow(
                        window_id=tw_id,
                        period_start=min_date,
                        period_end=max_date,
                        temporal_status="KNOWN",
                        resolution_notes=f"Período detectado: {min_date} a {max_date}.",
                    )
            else:
                # Columna fecha existe pero sin valores parseables
                temporal_window = TemporalWindow(
                    window_id=tw_id,
                    temporal_status="PARTIAL",
                    resolution_notes="Columna fecha presente pero sin valores parseables.",
                )
                alerts.append(NormalizationAlert(
                    alert_id=f"alert_temporal_partial_{document_id}",
                    alert_type="TEMPORAL_UNKNOWN",
                    ambiguity_level="HIGH",
                    description="Columna fecha presente pero sin valores de fecha válidos.",
                    suggested_action="Verificar el formato de fechas en el documento.",
                ))
        else:
            # Sin columna fecha
            temporal_window = TemporalWindow(
                window_id=tw_id,
                temporal_status="UNKNOWN",
                resolution_notes="No se detectó columna de fecha en el documento.",
            )
            alerts.append(NormalizationAlert(
                alert_id=f"alert_temporal_unknown_{document_id}",
                alert_type="TEMPORAL_UNKNOWN",
                ambiguity_level="HIGH",
                description="No se detectó columna de fecha. Sin ventana temporal no hay variable investigable.",
                suggested_action="Agregar columna de fecha o indicar el período que cubre el documento.",
            ))

        # --- Paso 5: EntityMentions y CanonicalEntities ---
        entity_mentions: list[EntityMention] = []
        canonical_entities: list[CanonicalEntity] = []

        if has_product_col and rows:
            raw_prod_col = canonical_to_raw["producto"]
            seen_products: dict[str, str] = {}  # raw_name → entity_id

            for i, row in enumerate(rows):
                raw_val = str(row.get(raw_prod_col, "")).strip()
                if not raw_val:
                    continue

                mention_id = f"mention_prod_{document_id}_{i}"
                entity_mention = EntityMention(
                    mention_id=mention_id,
                    raw_document_id=document_id,
                    raw_value=raw_val,
                    entity_type_candidate="producto",
                    source_field=raw_prod_col,
                    source_row=i,
                    confidence=0.82,
                    resolution_status="PENDING",
                )
                entity_mentions.append(entity_mention)

                # Crear entidad canónica por producto único (sin resolución avanzada)
                if raw_val not in seen_products:
                    entity_id = f"entity_prod_{document_id}_{len(seen_products)}"
                    seen_products[raw_val] = entity_id

                    alias = EntityAlias(
                        alias_id=f"alias_{entity_id}",
                        canonical_entity_id=entity_id,
                        raw_name=raw_val,
                        source_document_id=document_id,
                        source_field=raw_prod_col,
                        confidence=0.82,
                    )
                    canonical_entity = CanonicalEntity(
                        entity_id=entity_id,
                        cliente_id=cliente_id,
                        entity_type="producto",
                        canonical_name=raw_val,  # nombre crudo como canónico provisional
                        aliases=[alias],
                        sources=[document_id],
                        confidence=0.82,
                        requires_confirmation=True,
                    )
                    canonical_entities.append(canonical_entity)

        elif not has_product_col:
            # Sin columna producto → alerta, no se inventa entidad
            alerts.append(NormalizationAlert(
                alert_id=f"alert_no_product_{document_id}",
                alert_type="ENTITY_UNRESOLVED",
                ambiguity_level="MEDIUM",
                description="No se detectó columna de producto/entidad. Las variables no tendrán entidad asociada.",
                suggested_action="Agregar columna de producto o indicar a qué entidad aplican los datos.",
            ))

        # --- Paso 6: EvidenceReferences y CleanVariables ---
        evidence_refs: list[EvidenceReference] = []
        clean_variables: list[CleanVariable] = []

        # Solo generar variables si hay tiempo (KNOWN o PARTIAL) y columnas suficientes
        temporal_ok = temporal_window.temporal_status in ("KNOWN", "PARTIAL")

        if has_cantidad_col and rows:
            raw_cant_col = canonical_to_raw["cantidad"]

            for i, row in enumerate(rows):
                raw_val = str(row.get(raw_cant_col, "")).strip()
                if not raw_val:
                    continue

                parsed_num = _try_parse_number(raw_val)
                ref_id = f"ref_cant_{document_id}_{i}"

                ev_ref = EvidenceReference(
                    evidence_ref_id=ref_id,
                    source_document_id=document_id,
                    source_field=raw_cant_col,
                    source_row=i,
                    raw_value=raw_val,
                    normalized_value=parsed_num,
                    unit="unidades",
                    transformation_notes="Parseado como número desde string.",
                )
                evidence_refs.append(ev_ref)

                # Determinar entity_id si hay producto en la misma fila
                entity_id: Optional[str] = None
                if has_product_col:
                    raw_prod_col = canonical_to_raw["producto"]
                    prod_val = str(row.get(raw_prod_col, "")).strip()
                    # Buscar en canonical_entities
                    for ce in canonical_entities:
                        if ce.canonical_name == prod_val:
                            entity_id = ce.entity_id
                            break

                var_status = "NEEDS_REVIEW" if temporal_ok else "BLOCKED"
                var_notes = (
                    None if temporal_ok
                    else "Sin ventana temporal válida. Variable no usable en investigación."
                )

                clean_var = CleanVariable(
                    variable_id=f"var_cant_{document_id}_{i}",
                    canonical_name="cantidad",
                    entity_id=entity_id,
                    value=parsed_num,
                    unit="unidades",
                    evidence_ref_id=ref_id,
                    temporal_window=temporal_window,
                    confidence=0.82 if parsed_num is not None else 0.3,
                    status=var_status,  # type: ignore[arg-type]
                    notes=var_notes,
                )
                clean_variables.append(clean_var)

        if has_precio_col and rows:
            raw_precio_col = canonical_to_raw["precio_unitario"]

            for i, row in enumerate(rows):
                raw_val = str(row.get(raw_precio_col, "")).strip()
                if not raw_val:
                    continue

                parsed_num = _try_parse_number(raw_val)
                ref_id = f"ref_precio_{document_id}_{i}"

                ev_ref = EvidenceReference(
                    evidence_ref_id=ref_id,
                    source_document_id=document_id,
                    source_field=raw_precio_col,
                    source_row=i,
                    raw_value=raw_val,
                    normalized_value=parsed_num,
                    unit="ARS",
                    transformation_notes="Parseado como número desde string.",
                )
                evidence_refs.append(ev_ref)

                entity_id = None
                if has_product_col:
                    raw_prod_col = canonical_to_raw["producto"]
                    prod_val = str(row.get(raw_prod_col, "")).strip()
                    for ce in canonical_entities:
                        if ce.canonical_name == prod_val:
                            entity_id = ce.entity_id
                            break

                var_status = "NEEDS_REVIEW" if temporal_ok else "BLOCKED"
                var_notes = (
                    None if temporal_ok
                    else "Sin ventana temporal válida. Variable no usable en investigación."
                )

                clean_var = CleanVariable(
                    variable_id=f"var_precio_{document_id}_{i}",
                    canonical_name="precio_unitario",
                    entity_id=entity_id,
                    value=parsed_num,
                    unit="ARS",
                    evidence_ref_id=ref_id,
                    temporal_window=temporal_window,
                    confidence=0.80 if parsed_num is not None else 0.3,
                    status=var_status,  # type: ignore[arg-type]
                    notes=var_notes,
                )
                clean_variables.append(clean_var)

        # --- Paso 7: Determinar status del paquete ---
        has_temporal_alert = any(a.alert_type == "TEMPORAL_UNKNOWN" for a in alerts)
        has_clean_vars = len(clean_variables) > 0
        has_usable_vars = any(v.status in ("CLEAN", "NEEDS_REVIEW") for v in clean_variables)

        if has_usable_vars and not has_temporal_alert:
            pkg_status = "READY"
        elif has_usable_vars or (has_clean_vars and has_temporal_alert):
            pkg_status = "PARTIAL"
        else:
            pkg_status = "BLOCKED"

        blocking_reasons: list[str] = []
        if pkg_status == "BLOCKED":
            if not has_cantidad_col and not has_precio_col:
                blocking_reasons.append(
                    "No se detectaron columnas de cantidad ni precio. Sin variables investigables."
                )
            if has_temporal_alert:
                blocking_reasons.append(
                    "Sin ventana temporal no hay variable investigable."
                )

        # --- Paso 8: next_step ---
        if pkg_status == "READY":
            next_step = (
                "Evidencia normalizada lista. Capa 2 puede activar conocimiento e investigación."
            )
        elif pkg_status == "PARTIAL":
            pending = [a.description for a in alerts if not a.resolved]
            next_step = (
                "Evidencia parcialmente normalizada. Quedan ambigüedades pendientes: "
                + "; ".join(pending[:2])
                + ("..." if len(pending) > 2 else "")
            )
        else:
            next_step = (
                "No hay suficiente evidencia normalizada para investigar. "
                + " ".join(blocking_reasons)
            )

        return NormalizedEvidencePackage(
            package_id=package_id,
            cliente_id=cliente_id,
            source_admission_case_id=source_admission_case_id,
            created_at=datetime.utcnow(),
            documents=[raw_doc],
            schemas=[doc_schema],
            column_candidates=column_candidates,
            entity_mentions=entity_mentions,
            canonical_entities=canonical_entities,
            field_mappings=field_mappings,
            evidence_refs=evidence_refs,
            clean_variables=clean_variables,
            alerts=alerts,
            status=pkg_status,  # type: ignore[arg-type]
            blocking_reasons=blocking_reasons,
            next_step=next_step,
        )
