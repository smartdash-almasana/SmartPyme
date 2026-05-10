"""
Tests para app/contracts/bem_payloads.py

Cubre: creación válida, validaciones fail-closed, enums, metadata, confidence.
"""
from __future__ import annotations

import pytest

from app.contracts.bem_payloads import (
    BemConfidenceScore,
    BemSourceMetadata,
    CuratedEvidenceRecord,
    EvidenceKind,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _valid_metadata() -> BemSourceMetadata:
    return BemSourceMetadata(
        source_name="ventas_2024.xlsx",
        source_type="excel",
        uploaded_at="2024-01-15T10:00:00Z",
        external_reference_id="bem-ref-001",
    )


def _valid_record(**overrides) -> CuratedEvidenceRecord:
    defaults = dict(
        tenant_id="tenant-abc",
        evidence_id="ev-001",
        kind=EvidenceKind.EXCEL,
        payload={"rows": 100, "sheet": "Ventas"},
        source_metadata=_valid_metadata(),
        received_at="2024-01-15T10:05:00Z",
        confidence=BemConfidenceScore(score=0.95, provider="bem-v1"),
        trace_id="trace-xyz",
    )
    defaults.update(overrides)
    return CuratedEvidenceRecord(**defaults)


# ---------------------------------------------------------------------------
# EvidenceKind
# ---------------------------------------------------------------------------


def test_evidence_kind_has_expected_values():
    assert {item.value for item in EvidenceKind} == {
        "excel",
        "pdf",
        "image",
        "email",
        "audio",
        "mixed",
    }


def test_evidence_kind_is_str_enum():
    assert EvidenceKind.EXCEL == "excel"
    assert EvidenceKind.PDF == "pdf"


# ---------------------------------------------------------------------------
# BemSourceMetadata
# ---------------------------------------------------------------------------


def test_bem_source_metadata_valid_creation():
    meta = BemSourceMetadata(
        source_name="archivo.pdf",
        source_type="pdf",
    )
    assert meta.source_name == "archivo.pdf"
    assert meta.source_type == "pdf"
    assert meta.uploaded_at is None
    assert meta.external_reference_id is None


def test_bem_source_metadata_with_all_fields():
    meta = _valid_metadata()
    assert meta.uploaded_at == "2024-01-15T10:00:00Z"
    assert meta.external_reference_id == "bem-ref-001"


def test_bem_source_metadata_rejects_empty_source_name():
    with pytest.raises(ValueError, match="source_name"):
        BemSourceMetadata(source_name="", source_type="excel")


def test_bem_source_metadata_rejects_whitespace_source_name():
    with pytest.raises(ValueError, match="source_name"):
        BemSourceMetadata(source_name="   ", source_type="excel")


def test_bem_source_metadata_rejects_empty_source_type():
    with pytest.raises(ValueError, match="source_type"):
        BemSourceMetadata(source_name="archivo.xlsx", source_type="")


# ---------------------------------------------------------------------------
# BemConfidenceScore
# ---------------------------------------------------------------------------


def test_bem_confidence_score_valid():
    cs = BemConfidenceScore(score=0.85, provider="bem-v2")
    assert cs.score == 0.85
    assert cs.provider == "bem-v2"


def test_bem_confidence_score_boundary_zero():
    cs = BemConfidenceScore(score=0.0)
    assert cs.score == 0.0


def test_bem_confidence_score_boundary_one():
    cs = BemConfidenceScore(score=1.0)
    assert cs.score == 1.0


def test_bem_confidence_score_rejects_above_one():
    with pytest.raises(ValueError, match="score"):
        BemConfidenceScore(score=1.01)


def test_bem_confidence_score_rejects_below_zero():
    with pytest.raises(ValueError, match="score"):
        BemConfidenceScore(score=-0.01)


def test_bem_confidence_score_rejects_non_numeric():
    with pytest.raises(TypeError, match="score"):
        BemConfidenceScore(score="alto")  # type: ignore[arg-type]


def test_bem_confidence_score_provider_optional():
    cs = BemConfidenceScore(score=0.5)
    assert cs.provider is None


# ---------------------------------------------------------------------------
# CuratedEvidenceRecord — creación válida
# ---------------------------------------------------------------------------


def test_curated_evidence_record_valid_creation():
    record = _valid_record()
    assert record.tenant_id == "tenant-abc"
    assert record.evidence_id == "ev-001"
    assert record.kind == EvidenceKind.EXCEL
    assert record.payload == {"rows": 100, "sheet": "Ventas"}
    assert record.received_at == "2024-01-15T10:05:00Z"
    assert record.trace_id == "trace-xyz"


def test_curated_evidence_record_without_optional_fields():
    record = CuratedEvidenceRecord(
        tenant_id="tenant-1",
        evidence_id="ev-002",
        kind=EvidenceKind.PDF,
        payload={"pages": 5},
        source_metadata=_valid_metadata(),
        received_at="2024-01-15T11:00:00Z",
    )
    assert record.confidence is None
    assert record.trace_id is None


# ---------------------------------------------------------------------------
# CuratedEvidenceRecord — validaciones fail-closed
# ---------------------------------------------------------------------------


def test_curated_evidence_record_rejects_empty_tenant_id():
    with pytest.raises(ValueError, match="tenant_id"):
        _valid_record(tenant_id="")


def test_curated_evidence_record_rejects_whitespace_tenant_id():
    with pytest.raises(ValueError, match="tenant_id"):
        _valid_record(tenant_id="   ")


def test_curated_evidence_record_rejects_empty_evidence_id():
    with pytest.raises(ValueError, match="evidence_id"):
        _valid_record(evidence_id="")


def test_curated_evidence_record_rejects_empty_payload():
    with pytest.raises(ValueError, match="payload"):
        _valid_record(payload={})


def test_curated_evidence_record_rejects_none_payload():
    with pytest.raises((ValueError, TypeError)):
        _valid_record(payload=None)  # type: ignore[arg-type]


def test_curated_evidence_record_rejects_invalid_kind():
    with pytest.raises(TypeError, match="kind"):
        _valid_record(kind="excel")  # type: ignore[arg-type]


def test_curated_evidence_record_rejects_invalid_source_metadata():
    with pytest.raises(TypeError, match="source_metadata"):
        _valid_record(source_metadata={"source_name": "x"})  # type: ignore[arg-type]


def test_curated_evidence_record_rejects_invalid_confidence_type():
    with pytest.raises(TypeError, match="confidence"):
        _valid_record(confidence=0.9)  # type: ignore[arg-type]


def test_curated_evidence_record_accepts_all_evidence_kinds():
    for kind in EvidenceKind:
        record = _valid_record(kind=kind)
        assert record.kind == kind
