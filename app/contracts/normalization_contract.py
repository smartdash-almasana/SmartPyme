"""
Contratos Pydantic — Capa 1.5: Normalización Documental, Entidades y Tiempo
TS_015_001_CONTRATOS_NORMALIZACION

Modelos de datos mínimos para representar NormalizedEvidencePackage y sus
objetos componentes. Sin lógica de servicio, sin diagnóstico, sin OperationalCase.

Principios:
  - Sin tiempo no hay variable investigable.
  - Sin entidad canónica no hay comparación confiable.
  - Sin fuente trazable no hay hallazgo.
  - La evidencia cruda no se investiga directamente.

Documento rector:
  docs/product/SMARTPYME_CAPA_015_NORMALIZACION_DOCUMENTAL_ENTIDADES_TIEMPO.md
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field, model_validator


# ---------------------------------------------------------------------------
# Tipos literales
# ---------------------------------------------------------------------------

PackageStatus = Literal["READY", "PARTIAL", "BLOCKED"]
"""
Estado del NormalizedEvidencePackage.

READY   → toda la evidencia está normalizada; Capa 2 puede operar.
PARTIAL → hay variables limpias pero quedan ambigüedades; Capa 2 opera con alcance limitado.
BLOCKED → evidencia insuficiente; no habilita investigación.
"""

NormalizationStatus = Literal["READY", "PARTIAL", "BLOCKED"]
"""
Alias de PackageStatus para uso genérico en la capa.
"""

CleanVariableStatus = Literal["CLEAN", "NEEDS_REVIEW", "BLOCKED"]
"""
Estado de curación de una CleanVariable individual.

CLEAN        → variable lista para investigación.
NEEDS_REVIEW → variable usable pero requiere confirmación.
BLOCKED      → variable no usable; debe tener notes explicando el bloqueo.
"""

TemporalStatus = Literal["KNOWN", "PARTIAL", "UNKNOWN"]
"""
Estado de la ventana temporal de una variable.

KNOWN   → período o fecha completamente determinado.
PARTIAL → período parcialmente determinado; se asumió algo con base documental.
UNKNOWN → sin información temporal; la variable no puede usarse en investigación.
"""

ColumnStatus = Literal["CANDIDATE", "CONFIRMED", "DISCARDED", "AMBIGUOUS"]
"""
Estado de un ColumnCandidate.

CANDIDATE  → detectado automáticamente, pendiente de confirmación.
CONFIRMED  → confirmado manualmente.
DISCARDED  → descartado como irrelevante.
AMBIGUOUS  → ambiguo; requiere aclaración antes de usar.
"""

MappingStatus = Literal["CANDIDATE", "CONFIRMED", "DISCARDED"]
"""
Estado de un SourceFieldMapping.
"""

ResolutionStatus = Literal["PENDING", "RESOLVED", "UNRESOLVABLE"]
"""
Estado de resolución de una EntityMention.

PENDING      → aún no resuelta a entidad canónica.
RESOLVED     → resuelta; tiene canonical_entity_id.
UNRESOLVABLE → no se puede resolver con la evidencia disponible.
"""

ProcessingStatus = Literal["PENDING", "IN_PROGRESS", "DONE", "BLOCKED"]
"""
Estado de procesamiento de un RawDocument.
"""

SchemaStatus = Literal["CLEAN", "AMBIGUOUS", "BLOCKED"]
"""
Estado del DocumentSchema detectado.
"""

AmbiguityLevel = Literal["LOW", "MEDIUM", "HIGH"]
"""
Nivel de ambigüedad de una alerta de normalización.

LOW    → ambigüedad menor; no bloquea el procesamiento.
MEDIUM → ambigüedad significativa; requiere revisión.
HIGH   → ambigüedad crítica; puede bloquear la investigación.
"""

FileType = Literal["xlsx", "pdf", "csv", "txt", "image", "json", "xml", "whatsapp", "otro"]
"""
Tipo de archivo de un RawDocument.
"""

EntityType = Literal[
    "producto", "proveedor", "cliente", "empleado",
    "venta", "compra", "factura", "cuenta_bancaria",
    "caja", "sucursal", "documento", "otro"
]
"""
Tipo de entidad de negocio.
"""

VariableType = Literal[
    "stock", "precio", "venta", "gasto", "costo",
    "ingreso", "saldo", "cantidad", "margen", "otro"
]
"""
Tipo semántico de una CleanVariable.
"""


# ---------------------------------------------------------------------------
# TemporalWindow
# ---------------------------------------------------------------------------


class TemporalWindow(BaseModel):
    """
    Ventana temporal de una variable o evidencia.

    Toda variable investigable debe tener una TemporalWindow con al menos
    un campo temporal definido, o declarar temporal_status = UNKNOWN.

    Combinaciones válidas:
      - Snapshot puntual:          observed_at
      - Dato acumulado:            period_start + period_end
      - Precio o condición vigente: valid_from (+ valid_to si venció)
      - Sin tiempo conocido:       temporal_status = UNKNOWN
    """

    window_id: str = Field(..., description="Identificador único de la ventana temporal.")
    observed_at: Optional[date] = Field(
        default=None,
        description="Fecha de observación puntual: snapshot, inventario, saldo.",
    )
    period_start: Optional[date] = Field(
        default=None,
        description="Inicio del período cubierto por un dato acumulado.",
    )
    period_end: Optional[date] = Field(
        default=None,
        description="Fin del período cubierto por un dato acumulado.",
    )
    valid_from: Optional[date] = Field(
        default=None,
        description="Inicio de vigencia de un precio, condición o regla.",
    )
    valid_to: Optional[date] = Field(
        default=None,
        description="Fin de vigencia. None significa vigente hasta nuevo aviso.",
    )
    temporal_status: TemporalStatus = Field(
        default="UNKNOWN",
        description="Estado de la ventana temporal.",
    )
    resolution_notes: Optional[str] = Field(
        default=None,
        description="Cómo se determinó la ventana o qué se asumió.",
    )


# ---------------------------------------------------------------------------
# EvidenceReference
# ---------------------------------------------------------------------------


class EvidenceReference(BaseModel):
    """
    Referencia trazable que vincula una CleanVariable con su origen exacto
    en el documento fuente.

    Sin EvidenceReference no hay trazabilidad.
    Sin trazabilidad no hay hallazgo válido.
    """

    evidence_ref_id: str = Field(..., description="Identificador único de la referencia.")
    source_document_id: str = Field(
        ..., description="ID del RawDocument de origen."
    )
    source_field: str = Field(
        ..., description="Columna o campo original: 'cant.', 'precio', etc."
    )
    source_row: Optional[int] = Field(
        default=None, description="Fila de origen en el documento (si aplica)."
    )
    source_sheet: Optional[str] = Field(
        default=None, description="Hoja de origen en el documento (si aplica)."
    )
    raw_value: str = Field(
        ..., description="Valor original sin modificar, como string."
    )
    normalized_value: Optional[Any] = Field(
        default=None,
        description="Valor después de normalización (número, fecha, string limpio).",
    )
    unit: Optional[str] = Field(
        default=None, description="Unidad de medida si aplica: unidades, ARS, kg, etc."
    )
    transformation_notes: Optional[str] = Field(
        default=None,
        description="Descripción de qué transformación se aplicó al valor original.",
    )


# ---------------------------------------------------------------------------
# EntityAlias
# ---------------------------------------------------------------------------


class EntityAlias(BaseModel):
    """
    Nombre alternativo de una entidad canónica, con trazabilidad a su fuente.

    Los aliases conservan los nombres originales para que cualquier hallazgo
    pueda rastrearse hasta el documento de origen.
    """

    alias_id: str = Field(..., description="Identificador único del alias.")
    canonical_entity_id: str = Field(
        ..., description="ID de la CanonicalEntity a la que pertenece este alias."
    )
    raw_name: str = Field(
        ..., description="Nombre original tal como aparece en el documento: 'TSM', 'prov. SM'."
    )
    source_document_id: str = Field(
        ..., description="ID del RawDocument donde apareció este alias."
    )
    source_field: Optional[str] = Field(
        default=None, description="Campo o columna de origen."
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confianza en que este alias corresponde a la entidad canónica. Rango [0, 1].",
    )


# ---------------------------------------------------------------------------
# CanonicalEntity
# ---------------------------------------------------------------------------


class CanonicalEntity(BaseModel):
    """
    Entidad normalizada con nombre canónico y aliases trazables.

    La entidad canónica no borra los nombres originales.
    Los conserva como aliases para trazabilidad completa.
    """

    entity_id: str = Field(..., description="Identificador único de la entidad canónica.")
    cliente_id: str = Field(..., description="Tenant al que pertenece la entidad.")
    entity_type: EntityType = Field(..., description="Tipo de entidad de negocio.")
    canonical_name: str = Field(
        ..., description="Nombre canónico elegido para esta entidad."
    )
    aliases: list[EntityAlias] = Field(
        default_factory=list,
        description="Nombres alternativos con trazabilidad a sus fuentes originales.",
    )
    sources: list[str] = Field(
        default_factory=list,
        description="IDs de RawDocument que mencionan esta entidad.",
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confianza en la resolución canónica. Rango [0, 1].",
    )
    requires_confirmation: bool = Field(
        default=True,
        description="Si la entidad requiere confirmación manual antes de usarse.",
    )
    confirmed_by: Optional[str] = Field(
        default=None,
        description="person_id que confirmó la entidad manualmente.",
    )
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)


# ---------------------------------------------------------------------------
# EntityMention
# ---------------------------------------------------------------------------


class EntityMention(BaseModel):
    """
    Mención de una entidad tal como aparece en el documento, antes de
    resolución canónica.

    Las menciones son el insumo para construir CanonicalEntity.
    """

    mention_id: str = Field(..., description="Identificador único de la mención.")
    raw_document_id: str = Field(..., description="ID del RawDocument de origen.")
    raw_value: str = Field(
        ..., description="Texto original: 'TSM', 'Textil San Martin', 'PJ-AZ-42'."
    )
    entity_type_candidate: EntityType = Field(
        ..., description="Tipo de entidad probable."
    )
    source_field: Optional[str] = Field(
        default=None, description="Columna o campo de origen."
    )
    source_row: Optional[int] = Field(
        default=None, description="Fila de origen."
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confianza en la detección de la mención. Rango [0, 1].",
    )
    resolution_status: ResolutionStatus = Field(
        default="PENDING",
        description="Estado de resolución a entidad canónica.",
    )
    canonical_entity_id: Optional[str] = Field(
        default=None,
        description="ID de la CanonicalEntity si ya fue resuelta.",
    )


# ---------------------------------------------------------------------------
# ColumnCandidate
# ---------------------------------------------------------------------------


class ColumnCandidate(BaseModel):
    """
    Columna detectada en un documento con su posible significado semántico.

    Las columnas con confianza baja o ambigüedad alta se marcan para
    confirmación antes de usarse en mapeos.
    """

    column_candidate_id: str = Field(..., description="Identificador único del candidato.")
    schema_id: str = Field(..., description="ID del DocumentSchema de origen.")
    raw_column: str = Field(
        ..., description="Nombre original de la columna: 'prov.', 'cant.', '$'."
    )
    possible_meaning: Optional[str] = Field(
        default=None,
        description="Significado semántico candidato: 'proveedor', 'cantidad', 'precio_unitario'.",
    )
    data_type: Optional[Literal["string", "number", "date", "boolean", "mixed"]] = Field(
        default=None, description="Tipo de dato detectado en la columna."
    )
    sample_values: list[str] = Field(
        default_factory=list,
        description="Muestra de valores reales de la columna para contexto.",
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confianza en el mapeo semántico candidato. Rango [0, 1].",
    )
    requires_confirmation: bool = Field(
        default=True,
        description="Si el mapeo requiere confirmación manual.",
    )
    confirmed_by: Optional[str] = Field(
        default=None,
        description="person_id que confirmó el mapeo manualmente.",
    )
    status: ColumnStatus = Field(
        default="CANDIDATE",
        description="Estado del candidato de columna.",
    )


# ---------------------------------------------------------------------------
# SourceFieldMapping
# ---------------------------------------------------------------------------


class SourceFieldMapping(BaseModel):
    """
    Mapeo entre un campo crudo del documento y un campo semántico canónico
    del sistema.

    Permite que el sistema entienda qué significa cada columna del documento
    en términos del modelo de datos de SmartPyme.
    """

    mapping_id: str = Field(..., description="Identificador único del mapeo.")
    schema_id: str = Field(..., description="ID del DocumentSchema de origen.")
    raw_column: str = Field(
        ..., description="Nombre original de la columna: 'prov.'."
    )
    canonical_field: str = Field(
        ..., description="Nombre canónico del campo: 'proveedor'."
    )
    canonical_field_type: Optional[str] = Field(
        default=None,
        description="Tipo semántico del campo canónico: 'entity_ref', 'amount', 'date', etc.",
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confianza en el mapeo. Rango [0, 1].",
    )
    requires_confirmation: bool = Field(default=True)
    confirmed_by: Optional[str] = Field(default=None)
    status: MappingStatus = Field(default="CANDIDATE")


# ---------------------------------------------------------------------------
# DocumentSchema
# ---------------------------------------------------------------------------


class DocumentSchema(BaseModel):
    """
    Esquema detectado en un documento: columnas, tipos, estructura general.

    Cada RawDocument debe producir un DocumentSchema o un bloqueo documentado.
    """

    schema_id: str = Field(..., description="Identificador único del esquema.")
    raw_document_id: str = Field(..., description="ID del RawDocument de origen.")
    detected_columns: list[ColumnCandidate] = Field(
        default_factory=list,
        description="Columnas detectadas con sus candidatos semánticos.",
    )
    detected_entity_types: list[EntityType] = Field(
        default_factory=list,
        description="Tipos de entidades detectadas en el documento.",
    )
    row_count: Optional[int] = Field(
        default=None, description="Número de filas detectadas."
    )
    has_header: Optional[bool] = Field(
        default=None, description="Si el documento tiene fila de encabezado."
    )
    sheet_name: Optional[str] = Field(
        default=None, description="Nombre de la hoja si aplica (Excel)."
    )
    detection_confidence: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Confianza general en el esquema detectado.",
    )
    ambiguities: list[str] = Field(
        default_factory=list,
        description="Lista de ambigüedades detectadas en el esquema.",
    )
    schema_status: SchemaStatus = Field(
        default="AMBIGUOUS",
        description="Estado del esquema: CLEAN, AMBIGUOUS o BLOCKED.",
    )


# ---------------------------------------------------------------------------
# RawDocument
# ---------------------------------------------------------------------------


class RawDocument(BaseModel):
    """
    Documento recibido tal como llegó, sin modificar.

    Todo documento debe registrarse como RawDocument antes de cualquier
    procesamiento. Es el punto de entrada de la Capa 1.5.
    """

    raw_document_id: str = Field(..., description="Identificador único del documento.")
    cliente_id: str = Field(..., description="Tenant al que pertenece el documento.")
    case_id: Optional[str] = Field(
        default=None,
        description="ID del InitialCaseAdmission al que pertenece este documento.",
    )
    evidence_item_id: Optional[str] = Field(
        default=None,
        description="ID del EvidenceItem de Capa 01 que originó la solicitud de este documento.",
    )
    filename: str = Field(..., description="Nombre original del archivo.")
    file_type: FileType = Field(..., description="Tipo de archivo.")
    received_at: Optional[datetime] = Field(
        default=None, description="Timestamp de recepción del documento."
    )
    received_from: Optional[str] = Field(
        default=None,
        description="person_id o canal de origen del documento.",
    )
    file_hash: Optional[str] = Field(
        default=None,
        description="Hash SHA-256 del archivo para verificación de integridad.",
    )
    size_bytes: Optional[int] = Field(
        default=None, description="Tamaño del archivo en bytes."
    )
    raw_content_ref: Optional[str] = Field(
        default=None,
        description="Referencia al contenido almacenado (ruta, URI, ID de storage).",
    )
    processing_status: ProcessingStatus = Field(
        default="PENDING",
        description="Estado de procesamiento del documento.",
    )
    notes: Optional[str] = Field(default=None, description="Observaciones adicionales.")


# ---------------------------------------------------------------------------
# CleanVariable
# ---------------------------------------------------------------------------


class CleanVariable(BaseModel):
    """
    Variable investigable: limpia, trazable, con entidad canónica y ventana temporal.

    Es el output fundamental de la Capa 1.5 y el insumo principal de la Capa 2.

    Regla: si status = BLOCKED, notes es obligatorio para explicar el bloqueo.
    """

    variable_id: str = Field(..., description="Identificador único de la variable.")
    canonical_name: str = Field(
        ...,
        description="Nombre semántico canónico de la variable: 'stock_actual', 'precio_unitario'.",
    )
    entity_id: Optional[str] = Field(
        default=None,
        description="ID de la CanonicalEntity a la que aplica esta variable.",
    )
    value: Optional[Any] = Field(
        default=None,
        description="Valor de la variable. Puede ser None si status=BLOCKED.",
    )
    unit: Optional[str] = Field(
        default=None,
        description="Unidad de medida: unidades, ARS, kg, horas, etc.",
    )
    evidence_ref_id: str = Field(
        ...,
        description="ID de la EvidenceReference que traza esta variable a su fuente.",
    )
    temporal_window: TemporalWindow = Field(
        ...,
        description="Ventana temporal de la variable. Obligatoria.",
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confianza en el valor y la normalización. Rango [0, 1].",
    )
    status: CleanVariableStatus = Field(
        default="NEEDS_REVIEW",
        description="Estado de curación: CLEAN, NEEDS_REVIEW o BLOCKED.",
    )
    notes: Optional[str] = Field(
        default=None,
        description="Observaciones. Obligatorio si status=BLOCKED.",
    )

    @model_validator(mode="after")
    def blocked_requires_notes(self) -> "CleanVariable":
        """Una variable BLOCKED debe tener notes explicando el bloqueo."""
        if self.status == "BLOCKED" and not self.notes:
            raise ValueError(
                "CleanVariable con status=BLOCKED debe incluir notes "
                "explicando la razón del bloqueo."
            )
        return self


# ---------------------------------------------------------------------------
# NormalizationAlert
# ---------------------------------------------------------------------------


class NormalizationAlert(BaseModel):
    """
    Alerta de ambigüedad o problema detectado durante la normalización.

    Las ambigüedades no se ocultan: se registran como alertas y se devuelven
    al dueño para confirmación.
    """

    alert_id: str = Field(..., description="Identificador único de la alerta.")
    alert_type: Literal[
        "COLUMN_AMBIGUOUS",
        "ENTITY_UNRESOLVED",
        "TEMPORAL_UNKNOWN",
        "MAPPING_CONFLICT",
        "MISSING_EVIDENCE",
        "LOW_CONFIDENCE",
        "OTHER",
    ] = Field(..., description="Tipo de alerta.")
    ambiguity_level: AmbiguityLevel = Field(
        ..., description="Nivel de ambigüedad: LOW, MEDIUM o HIGH."
    )
    description: str = Field(
        ..., description="Descripción concreta de la ambigüedad o problema."
    )
    affected_object_id: Optional[str] = Field(
        default=None,
        description="ID del objeto afectado: column_candidate_id, entity_id, etc.",
    )
    suggested_action: Optional[str] = Field(
        default=None,
        description="Acción sugerida para resolver la ambigüedad.",
    )
    resolved: bool = Field(
        default=False,
        description="Si la alerta fue resuelta.",
    )
    resolved_by: Optional[str] = Field(
        default=None,
        description="person_id que resolvió la alerta.",
    )


# ---------------------------------------------------------------------------
# NormalizedEvidencePackage
# ---------------------------------------------------------------------------


class NormalizedEvidencePackage(BaseModel):
    """
    Output exclusivo de la Capa 1.5: Normalización Documental, Entidades y Tiempo.

    Paquete completo de evidencia normalizada listo para ser consumido por Capa 2.

    Estados:
      READY   → Capa 2 puede operar sobre todas las variables.
      PARTIAL → Capa 2 puede operar con alcance limitado; hay alertas pendientes.
      BLOCKED → No habilita investigación; blocking_reasons explica qué falta.

    NO es un diagnóstico.
    NO contiene hallazgos.
    NO crea OperationalCase.
    """

    package_id: str = Field(..., description="Identificador único del paquete.")
    cliente_id: str = Field(..., description="Tenant al que pertenece el paquete.")
    source_admission_case_id: Optional[str] = Field(
        default=None,
        description="ID del InitialCaseAdmission que originó este paquete.",
    )
    created_at: Optional[datetime] = Field(
        default=None, description="Timestamp de creación del paquete."
    )
    documents: list[RawDocument] = Field(
        default_factory=list,
        description="Documentos crudos procesados en este paquete.",
    )
    schemas: list[DocumentSchema] = Field(
        default_factory=list,
        description="Esquemas detectados por documento.",
    )
    column_candidates: list[ColumnCandidate] = Field(
        default_factory=list,
        description="Candidatos de columna detectados.",
    )
    entity_mentions: list[EntityMention] = Field(
        default_factory=list,
        description="Menciones de entidades detectadas en los documentos.",
    )
    canonical_entities: list[CanonicalEntity] = Field(
        default_factory=list,
        description="Entidades canónicas resueltas.",
    )
    field_mappings: list[SourceFieldMapping] = Field(
        default_factory=list,
        description="Mapeos entre campos crudos y campos canónicos.",
    )
    evidence_refs: list[EvidenceReference] = Field(
        default_factory=list,
        description="Referencias trazables de variables a sus fuentes exactas.",
    )
    clean_variables: list[CleanVariable] = Field(
        default_factory=list,
        description="Variables investigables limpias, trazables y con ventana temporal.",
    )
    alerts: list[NormalizationAlert] = Field(
        default_factory=list,
        description="Alertas de ambigüedad o problemas pendientes de resolución.",
    )
    status: PackageStatus = Field(
        ...,
        description="Estado del paquete: READY, PARTIAL o BLOCKED.",
    )
    blocking_reasons: list[str] = Field(
        default_factory=list,
        description="Razones de bloqueo si status=BLOCKED.",
    )
    next_step: str = Field(
        ...,
        description="Instrucción técnica para Capa 02 o para el sistema.",
    )
