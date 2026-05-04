"""
Tests — NormalizationService mínimo
TS_015_002_NORMALIZATION_SERVICE_MINIMO

Valida el comportamiento determinístico de NormalizationService.process().

Casos:
  1. Excel Paulita completo → NormalizedEvidencePackage READY o PARTIAL con mappings.
  2. Detecta ColumnCandidate para "cant." como cantidad.
  3. Detecta ColumnCandidate para "prov." como proveedor.
  4. Produce CleanVariable con TemporalWindow cuando hay fecha.
  5. Si no hay fecha, agrega alerta temporal.
  6. Si falta columna producto, no inventa entidad y marca alerta.
  7. La salida siempre es NormalizedEvidencePackage.
  8. No aparece OperationalCase.
"""

import pytest

from app.contracts.normalization_contract import NormalizedEvidencePackage
from app.services.normalization_service import NormalizationService


# ---------------------------------------------------------------------------
# Fixtures de documentos de prueba
# ---------------------------------------------------------------------------

EXCEL_PAULITA_COMPLETO = {
    "cliente_id": "cliente_perales",
    "document_id": "excel_paulita",
    "source_type": "xlsx",
    "columns": ["fecha", "producto", "cant.", "precio", "prov."],
    "rows": [
        {"fecha": "2026-05-01", "producto": "PJ-AZ-42", "cant.": "120", "precio": "5500", "prov.": "TSM"},
        {"fecha": "2026-05-02", "producto": "PJ-AZ-44", "cant.": "85",  "precio": "5500", "prov.": "TSM"},
        {"fecha": "2026-05-03", "producto": "PJ-AZ-46", "cant.": "60",  "precio": "5800", "prov.": "TSM"},
    ],
}

EXCEL_SIN_FECHA = {
    "cliente_id": "cliente_perales",
    "document_id": "excel_sin_fecha",
    "source_type": "xlsx",
    "columns": ["producto", "cant.", "precio"],
    "rows": [
        {"producto": "PJ-AZ-42", "cant.": "120", "precio": "5500"},
        {"producto": "PJ-AZ-44", "cant.": "85",  "precio": "5500"},
    ],
}

EXCEL_SIN_PRODUCTO = {
    "cliente_id": "cliente_perales",
    "document_id": "excel_sin_producto",
    "source_type": "xlsx",
    "columns": ["fecha", "cant.", "precio"],
    "rows": [
        {"fecha": "2026-05-01", "cant.": "120", "precio": "5500"},
        {"fecha": "2026-05-02", "cant.": "85",  "precio": "5500"},
    ],
}

EXCEL_SOLO_COLUMNAS_DESCONOCIDAS = {
    "cliente_id": "cliente_x",
    "document_id": "excel_raro",
    "source_type": "xlsx",
    "columns": ["col_a", "col_b"],
    "rows": [
        {"col_a": "valor1", "col_b": "valor2"},
    ],
}


@pytest.fixture
def service() -> NormalizationService:
    return NormalizationService()


# ---------------------------------------------------------------------------
# Test 1: Excel Paulita completo → READY o PARTIAL con mappings
# ---------------------------------------------------------------------------


def test_excel_paulita_produces_package_ready_or_partial(service: NormalizationService):
    """Excel con fecha/producto/cant./precio/prov. debe producir READY o PARTIAL."""
    result = service.process(EXCEL_PAULITA_COMPLETO)
    assert result.status in ("READY", "PARTIAL")


def test_excel_paulita_has_field_mappings(service: NormalizationService):
    """El paquete debe tener SourceFieldMappings para las columnas reconocidas."""
    result = service.process(EXCEL_PAULITA_COMPLETO)
    assert len(result.field_mappings) > 0
    canonical_fields = [m.canonical_field for m in result.field_mappings]
    assert "cantidad" in canonical_fields
    assert "precio_unitario" in canonical_fields


def test_excel_paulita_has_clean_variables(service: NormalizationService):
    """El paquete debe tener CleanVariables generadas."""
    result = service.process(EXCEL_PAULITA_COMPLETO)
    assert len(result.clean_variables) > 0


def test_excel_paulita_has_evidence_refs(service: NormalizationService):
    """Cada CleanVariable debe tener una EvidenceReference trazable."""
    result = service.process(EXCEL_PAULITA_COMPLETO)
    ref_ids = {r.evidence_ref_id for r in result.evidence_refs}
    for var in result.clean_variables:
        assert var.evidence_ref_id in ref_ids, (
            f"Variable {var.variable_id} tiene evidence_ref_id={var.evidence_ref_id} "
            f"que no está en evidence_refs."
        )


# ---------------------------------------------------------------------------
# Test 2: Detecta ColumnCandidate para "cant." como cantidad
# ---------------------------------------------------------------------------


def test_detects_cant_as_cantidad(service: NormalizationService):
    """Columna 'cant.' debe detectarse como 'cantidad'."""
    result = service.process(EXCEL_PAULITA_COMPLETO)
    cant_candidates = [
        c for c in result.column_candidates
        if c.raw_column == "cant." and c.possible_meaning == "cantidad"
    ]
    assert len(cant_candidates) == 1
    assert cant_candidates[0].confidence > 0.9


# ---------------------------------------------------------------------------
# Test 3: Detecta ColumnCandidate para "prov." como proveedor
# ---------------------------------------------------------------------------


def test_detects_prov_as_proveedor(service: NormalizationService):
    """Columna 'prov.' debe detectarse como 'proveedor'."""
    result = service.process(EXCEL_PAULITA_COMPLETO)
    prov_candidates = [
        c for c in result.column_candidates
        if c.raw_column == "prov." and c.possible_meaning == "proveedor"
    ]
    assert len(prov_candidates) == 1
    assert prov_candidates[0].confidence > 0.7


# ---------------------------------------------------------------------------
# Test 4: Produce CleanVariable con TemporalWindow cuando hay fecha
# ---------------------------------------------------------------------------


def test_clean_variable_has_temporal_window_when_fecha_present(service: NormalizationService):
    """Con columna fecha, las CleanVariables deben tener TemporalWindow con status KNOWN."""
    result = service.process(EXCEL_PAULITA_COMPLETO)
    assert len(result.clean_variables) > 0
    for var in result.clean_variables:
        assert var.temporal_window is not None
        assert var.temporal_window.temporal_status in ("KNOWN", "PARTIAL")


def test_temporal_window_period_detected_from_multiple_dates(service: NormalizationService):
    """Con múltiples fechas distintas, debe detectar period_start y period_end."""
    result = service.process(EXCEL_PAULITA_COMPLETO)
    # El Excel tiene fechas 2026-05-01 a 2026-05-03
    tw = result.clean_variables[0].temporal_window
    # Puede ser period_start/end o observed_at según implementación
    has_period = tw.period_start is not None and tw.period_end is not None
    has_observed = tw.observed_at is not None
    assert has_period or has_observed


# ---------------------------------------------------------------------------
# Test 5: Si no hay fecha, agrega alerta temporal
# ---------------------------------------------------------------------------


def test_no_fecha_column_adds_temporal_alert(service: NormalizationService):
    """Sin columna fecha debe agregar alerta de tipo TEMPORAL_UNKNOWN."""
    result = service.process(EXCEL_SIN_FECHA)
    temporal_alerts = [a for a in result.alerts if a.alert_type == "TEMPORAL_UNKNOWN"]
    assert len(temporal_alerts) > 0


def test_no_fecha_temporal_window_is_unknown(service: NormalizationService):
    """Sin columna fecha, las variables deben tener temporal_status=UNKNOWN."""
    result = service.process(EXCEL_SIN_FECHA)
    for var in result.clean_variables:
        assert var.temporal_window.temporal_status == "UNKNOWN"


# ---------------------------------------------------------------------------
# Test 6: Si falta columna producto, no inventa entidad y marca alerta
# ---------------------------------------------------------------------------


def test_no_product_column_adds_entity_alert(service: NormalizationService):
    """Sin columna producto debe agregar alerta ENTITY_UNRESOLVED."""
    result = service.process(EXCEL_SIN_PRODUCTO)
    entity_alerts = [a for a in result.alerts if a.alert_type == "ENTITY_UNRESOLVED"]
    assert len(entity_alerts) > 0


def test_no_product_column_no_canonical_entities(service: NormalizationService):
    """Sin columna producto no debe crear CanonicalEntities de tipo producto."""
    result = service.process(EXCEL_SIN_PRODUCTO)
    product_entities = [e for e in result.canonical_entities if e.entity_type == "producto"]
    assert len(product_entities) == 0


def test_no_product_column_variables_have_no_entity_id(service: NormalizationService):
    """Sin columna producto, las CleanVariables no deben tener entity_id."""
    result = service.process(EXCEL_SIN_PRODUCTO)
    for var in result.clean_variables:
        assert var.entity_id is None


# ---------------------------------------------------------------------------
# Test 7: La salida siempre es NormalizedEvidencePackage
# ---------------------------------------------------------------------------


def test_output_is_always_normalized_evidence_package(service: NormalizationService):
    """process() siempre debe retornar NormalizedEvidencePackage."""
    for doc in [
        EXCEL_PAULITA_COMPLETO,
        EXCEL_SIN_FECHA,
        EXCEL_SIN_PRODUCTO,
        EXCEL_SOLO_COLUMNAS_DESCONOCIDAS,
    ]:
        result = service.process(doc)
        assert isinstance(result, NormalizedEvidencePackage)


def test_output_has_required_fields(service: NormalizationService):
    """El paquete siempre debe tener package_id, cliente_id, status y next_step."""
    result = service.process(EXCEL_PAULITA_COMPLETO)
    assert result.package_id != ""
    assert result.cliente_id == "cliente_perales"
    assert result.status in ("READY", "PARTIAL", "BLOCKED")
    assert result.next_step.strip() != ""


# ---------------------------------------------------------------------------
# Test 8: No aparece OperationalCase
# ---------------------------------------------------------------------------


def test_no_operational_case_in_output(service: NormalizationService):
    """El output no debe tener atributos de OperationalCase."""
    result = service.process(EXCEL_PAULITA_COMPLETO)
    assert not hasattr(result, "hypothesis")
    assert not hasattr(result, "job_id")
    assert not hasattr(result, "skill_id")
    assert not hasattr(result, "diagnosis_status")


def test_no_operational_case_class_imported(service: NormalizationService):
    """NormalizationService no debe importar ni retornar OperationalCase."""
    import app.services.normalization_service as svc_module
    assert not hasattr(svc_module, "OperationalCase")


# ---------------------------------------------------------------------------
# Tests TS_015_004: Catálogo externo y catálogo custom
# ---------------------------------------------------------------------------


def test_cant_detected_from_external_catalog():
    """
    'cant.' debe detectarse como 'cantidad' cargando el catálogo externo por defecto.
    Confirma que NormalizationService() sin argumentos usa el JSON del catálogo.
    """
    # Instanciar sin argumentos → carga app/catalogs/column_mapping_catalog.json
    service = NormalizationService()
    result = service.process({
        "cliente_id": "cliente_catalog_test",
        "document_id": "doc_catalog_test",
        "source_type": "xlsx",
        "columns": ["cant.", "precio"],
        "rows": [{"cant.": "50", "precio": "1000"}],
    })
    cant_candidates = [
        c for c in result.column_candidates
        if c.raw_column == "cant." and c.possible_meaning == "cantidad"
    ]
    assert len(cant_candidates) == 1, (
        "El catálogo externo debe mapear 'cant.' a 'cantidad'."
    )
    assert cant_candidates[0].confidence > 0.9


def test_custom_catalog_is_respected():
    """
    Si se instancia NormalizationService con un column_map custom,
    debe usar ese catálogo y no el externo ni el fallback.
    """
    # Catálogo custom: solo reconoce "importe" como precio_unitario
    custom_map: dict[str, tuple[str, float, str, bool]] = {
        "importe": ("precio_unitario", 0.99, "amount", False),
        "fecha":   ("fecha",           0.90, "date",   False),
    }
    service = NormalizationService(column_map=custom_map)
    result = service.process({
        "cliente_id": "cliente_custom",
        "document_id": "doc_custom",
        "source_type": "xlsx",
        "columns": ["fecha", "importe", "cant."],
        "rows": [{"fecha": "2026-05-01", "importe": "5500", "cant.": "10"}],
    })

    # "importe" debe mapearse a precio_unitario
    importe_mappings = [
        m for m in result.field_mappings if m.raw_column == "importe"
    ]
    assert len(importe_mappings) == 1
    assert importe_mappings[0].canonical_field == "precio_unitario"

    # "cant." NO debe reconocerse (no está en el catálogo custom)
    cant_mappings = [
        m for m in result.field_mappings if m.raw_column == "cant."
    ]
    assert len(cant_mappings) == 0, (
        "Con catálogo custom que no incluye 'cant.', no debe generarse mapping para esa columna."
    )
