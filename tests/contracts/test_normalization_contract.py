"""
Tests — Contratos Pydantic Capa 1.5: Normalización Documental, Entidades y Tiempo
TS_015_001_CONTRATOS_NORMALIZACION

Valida los contratos definidos en app/contracts/normalization_contract.py.

Cobertura requerida:
  1. Construir NormalizedEvidencePackage válido completo.
  2. CleanVariable.confidence rechaza <0 y >1.
  3. ColumnCandidate.confidence rechaza <0 y >1.
  4. EntityAlias conserva alias original y canonical_entity_id.
  5. TemporalWindow permite observed_at o period_start/period_end.
  6. CleanVariable BLOCKED puede no tener value pero debe tener notes.
  7. NormalizedEvidencePackage.status rechaza valores inválidos.
  8. NormalizationAlert puede marcar ambigüedad HIGH.
"""

from datetime import date, datetime

import pytest
from pydantic import ValidationError

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
# Fixtures de objetos mínimos válidos
# ---------------------------------------------------------------------------


def _valid_temporal_window(window_id: str = "tw_001") -> TemporalWindow:
    return TemporalWindow(
        window_id=window_id,
        observed_at=date(2026, 5, 3),
        temporal_status="KNOWN",
    )


def _valid_evidence_ref(ref_id: str = "ref_001") -> EvidenceReference:
    return EvidenceReference(
        evidence_ref_id=ref_id,
        source_document_id="doc_001",
        source_field="cant.",
        raw_value="120",
        normalized_value=120,
        unit="unidades",
    )


def _valid_clean_variable(var_id: str = "var_001") -> CleanVariable:
    return CleanVariable(
        variable_id=var_id,
        canonical_name="stock_actual",
        entity_id="entity_pantalon_001",
        value=120,
        unit="unidades",
        evidence_ref_id="ref_001",
        temporal_window=_valid_temporal_window(),
        confidence=0.82,
        status="CLEAN",
    )


def _valid_raw_document(doc_id: str = "doc_001") -> RawDocument:
    return RawDocument(
        raw_document_id=doc_id,
        cliente_id="cliente_perales",
        filename="stock_mayo_paulita.xlsx",
        file_type="xlsx",
        received_at=datetime(2026, 5, 3, 14, 22, 0),
    )


def _valid_column_candidate(col_id: str = "col_001") -> ColumnCandidate:
    return ColumnCandidate(
        column_candidate_id=col_id,
        schema_id="schema_001",
        raw_column="cant.",
        possible_meaning="cantidad",
        confidence=0.95,
        status="CONFIRMED",
        requires_confirmation=False,
    )


def _valid_entity_alias(alias_id: str = "alias_001", entity_id: str = "entity_001") -> EntityAlias:
    return EntityAlias(
        alias_id=alias_id,
        canonical_entity_id=entity_id,
        raw_name="TSM",
        source_document_id="doc_001",
        confidence=0.74,
    )


def _valid_canonical_entity(entity_id: str = "entity_001") -> CanonicalEntity:
    return CanonicalEntity(
        entity_id=entity_id,
        cliente_id="cliente_perales",
        entity_type="proveedor",
        canonical_name="Textiles San Martín",
        aliases=[_valid_entity_alias(entity_id=entity_id)],
        confidence=0.86,
    )


# ---------------------------------------------------------------------------
# Test 1: Construir NormalizedEvidencePackage válido completo
# ---------------------------------------------------------------------------


def test_normalized_evidence_package_valid_construction():
    """Un NormalizedEvidencePackage bien formado debe construirse sin errores."""
    doc = _valid_raw_document()
    schema = DocumentSchema(
        schema_id="schema_001",
        raw_document_id="doc_001",
        detected_columns=[_valid_column_candidate()],
        row_count=87,
        has_header=True,
        sheet_name="Stock_Mayo",
        schema_status="AMBIGUOUS",
        ambiguities=["prov. podría ser proveedor o vendedor"],
    )
    entity = _valid_canonical_entity()
    mention = EntityMention(
        mention_id="mention_001",
        raw_document_id="doc_001",
        raw_value="PJ-AZ-42",
        entity_type_candidate="producto",
        source_field="producto",
        source_row=14,
        confidence=0.82,
        resolution_status="RESOLVED",
        canonical_entity_id="entity_001",
    )
    mapping = SourceFieldMapping(
        mapping_id="map_001",
        schema_id="schema_001",
        raw_column="prov.",
        canonical_field="proveedor",
        confidence=0.78,
        status="CANDIDATE",
    )
    ref = _valid_evidence_ref()
    var = _valid_clean_variable()
    alert = NormalizationAlert(
        alert_id="alert_001",
        alert_type="COLUMN_AMBIGUOUS",
        ambiguity_level="MEDIUM",
        description="Columna 'prov.' podría ser proveedor o vendedor.",
        suggested_action="Confirmar con el dueño qué representa la columna.",
    )

    pkg = NormalizedEvidencePackage(
        package_id="pkg_perales_001",
        cliente_id="cliente_perales",
        source_admission_case_id="case_perales_001",
        created_at=datetime(2026, 5, 3, 15, 0, 0),
        documents=[doc],
        schemas=[schema],
        column_candidates=[_valid_column_candidate()],
        entity_mentions=[mention],
        canonical_entities=[entity],
        field_mappings=[mapping],
        evidence_refs=[ref],
        clean_variables=[var],
        alerts=[alert],
        status="PARTIAL",
        next_step="Confirmar si 'prov.' es proveedor o vendedor.",
    )

    assert pkg.package_id == "pkg_perales_001"
    assert pkg.cliente_id == "cliente_perales"
    assert pkg.status == "PARTIAL"
    assert len(pkg.documents) == 1
    assert len(pkg.clean_variables) == 1
    assert len(pkg.alerts) == 1
    assert pkg.next_step != ""


# ---------------------------------------------------------------------------
# Test 2: CleanVariable.confidence rechaza <0 y >1
# ---------------------------------------------------------------------------


def test_clean_variable_confidence_rejects_below_zero():
    """confidence < 0 debe lanzar ValidationError."""
    with pytest.raises(ValidationError):
        CleanVariable(
            variable_id="var_bad",
            canonical_name="stock_actual",
            evidence_ref_id="ref_001",
            temporal_window=_valid_temporal_window("tw_bad"),
            confidence=-0.1,
        )


def test_clean_variable_confidence_rejects_above_one():
    """confidence > 1 debe lanzar ValidationError."""
    with pytest.raises(ValidationError):
        CleanVariable(
            variable_id="var_bad",
            canonical_name="stock_actual",
            evidence_ref_id="ref_001",
            temporal_window=_valid_temporal_window("tw_bad"),
            confidence=1.1,
        )


# ---------------------------------------------------------------------------
# Test 3: ColumnCandidate.confidence rechaza <0 y >1
# ---------------------------------------------------------------------------


def test_column_candidate_confidence_rejects_below_zero():
    """confidence < 0 en ColumnCandidate debe lanzar ValidationError."""
    with pytest.raises(ValidationError):
        ColumnCandidate(
            column_candidate_id="col_bad",
            schema_id="schema_001",
            raw_column="cant.",
            confidence=-0.1,
        )


def test_column_candidate_confidence_rejects_above_one():
    """confidence > 1 en ColumnCandidate debe lanzar ValidationError."""
    with pytest.raises(ValidationError):
        ColumnCandidate(
            column_candidate_id="col_bad",
            schema_id="schema_001",
            raw_column="cant.",
            confidence=1.5,
        )


# ---------------------------------------------------------------------------
# Test 4: EntityAlias conserva alias original y canonical_entity_id
# ---------------------------------------------------------------------------


def test_entity_alias_preserves_raw_name_and_entity_id():
    """EntityAlias debe conservar raw_name y canonical_entity_id sin modificar."""
    alias = EntityAlias(
        alias_id="alias_tsm",
        canonical_entity_id="entity_textiles_san_martin",
        raw_name="TSM",
        source_document_id="doc_001",
        confidence=0.74,
    )
    assert alias.raw_name == "TSM"
    assert alias.canonical_entity_id == "entity_textiles_san_martin"


def test_canonical_entity_preserves_all_aliases():
    """CanonicalEntity debe conservar todos los aliases originales."""
    aliases = [
        EntityAlias(
            alias_id=f"alias_{i}",
            canonical_entity_id="entity_001",
            raw_name=name,
            source_document_id="doc_001",
            confidence=0.8,
        )
        for i, name in enumerate(["TSM", "Textil San Martin", "San Martín Textil"])
    ]
    entity = CanonicalEntity(
        entity_id="entity_001",
        cliente_id="cliente_x",
        entity_type="proveedor",
        canonical_name="Textiles San Martín",
        aliases=aliases,
        confidence=0.86,
    )
    raw_names = [a.raw_name for a in entity.aliases]
    assert "TSM" in raw_names
    assert "Textil San Martin" in raw_names
    assert "San Martín Textil" in raw_names
    assert len(entity.aliases) == 3


# ---------------------------------------------------------------------------
# Test 5: TemporalWindow permite observed_at o period_start/period_end
# ---------------------------------------------------------------------------


def test_temporal_window_with_observed_at():
    """TemporalWindow con observed_at debe construirse correctamente."""
    tw = TemporalWindow(
        window_id="tw_snapshot",
        observed_at=date(2026, 5, 3),
        temporal_status="KNOWN",
    )
    assert tw.observed_at == date(2026, 5, 3)
    assert tw.period_start is None
    assert tw.period_end is None


def test_temporal_window_with_period():
    """TemporalWindow con period_start y period_end debe construirse correctamente."""
    tw = TemporalWindow(
        window_id="tw_period",
        period_start=date(2026, 4, 1),
        period_end=date(2026, 4, 30),
        temporal_status="KNOWN",
    )
    assert tw.period_start == date(2026, 4, 1)
    assert tw.period_end == date(2026, 4, 30)
    assert tw.observed_at is None


def test_temporal_window_all_none_is_unknown():
    """TemporalWindow sin ningún campo temporal debe poder crearse con status UNKNOWN."""
    tw = TemporalWindow(
        window_id="tw_unknown",
        temporal_status="UNKNOWN",
    )
    assert tw.observed_at is None
    assert tw.period_start is None
    assert tw.period_end is None
    assert tw.temporal_status == "UNKNOWN"


# ---------------------------------------------------------------------------
# Test 6: CleanVariable BLOCKED puede no tener value pero debe tener notes
# ---------------------------------------------------------------------------


def test_clean_variable_blocked_without_value_requires_notes():
    """CleanVariable BLOCKED sin value debe requerir notes."""
    # Sin notes → debe fallar
    with pytest.raises(ValidationError, match="BLOCKED"):
        CleanVariable(
            variable_id="var_blocked",
            canonical_name="stock_actual",
            evidence_ref_id="ref_001",
            temporal_window=_valid_temporal_window("tw_blocked"),
            confidence=0.3,
            status="BLOCKED",
            value=None,
            notes=None,  # falta notes → error
        )


def test_clean_variable_blocked_with_notes_is_valid():
    """CleanVariable BLOCKED con notes debe construirse sin errores."""
    var = CleanVariable(
        variable_id="var_blocked_ok",
        canonical_name="stock_actual",
        evidence_ref_id="ref_001",
        temporal_window=_valid_temporal_window("tw_blocked_ok"),
        confidence=0.3,
        status="BLOCKED",
        value=None,
        notes="Columna 'fecha' sin año en 12 filas. No se puede asignar ventana temporal.",
    )
    assert var.status == "BLOCKED"
    assert var.value is None
    assert var.notes is not None


# ---------------------------------------------------------------------------
# Test 7: NormalizedEvidencePackage.status rechaza valores inválidos
# ---------------------------------------------------------------------------


def test_package_status_rejects_invalid_value():
    """status con valor fuera del Literal debe lanzar ValidationError."""
    with pytest.raises(ValidationError):
        NormalizedEvidencePackage(
            package_id="pkg_bad",
            cliente_id="cliente_x",
            status="INVALID_STATUS",  # type: ignore[arg-type]
            next_step="Siguiente paso.",
        )


def test_package_status_accepts_valid_values():
    """status READY, PARTIAL y BLOCKED deben ser aceptados."""
    for valid_status in ("READY", "PARTIAL", "BLOCKED"):
        pkg = NormalizedEvidencePackage(
            package_id=f"pkg_{valid_status.lower()}",
            cliente_id="cliente_x",
            status=valid_status,  # type: ignore[arg-type]
            next_step="Siguiente paso.",
        )
        assert pkg.status == valid_status


# ---------------------------------------------------------------------------
# Test 8: NormalizationAlert puede marcar ambigüedad HIGH
# ---------------------------------------------------------------------------


def test_normalization_alert_high_ambiguity():
    """NormalizationAlert con ambiguity_level=HIGH debe construirse correctamente."""
    alert = NormalizationAlert(
        alert_id="alert_high",
        alert_type="ENTITY_UNRESOLVED",
        ambiguity_level="HIGH",
        description=(
            "La entidad 'TSM' no pudo resolverse a ninguna entidad canónica. "
            "Puede ser proveedor o cliente."
        ),
        suggested_action="Confirmar con el dueño qué es 'TSM'.",
    )
    assert alert.ambiguity_level == "HIGH"
    assert alert.resolved is False


def test_normalization_alert_all_levels():
    """NormalizationAlert debe aceptar LOW, MEDIUM y HIGH."""
    for level in ("LOW", "MEDIUM", "HIGH"):
        alert = NormalizationAlert(
            alert_id=f"alert_{level.lower()}",
            alert_type="LOW_CONFIDENCE",
            ambiguity_level=level,  # type: ignore[arg-type]
            description=f"Alerta de nivel {level}.",
        )
        assert alert.ambiguity_level == level
