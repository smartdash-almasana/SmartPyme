from __future__ import annotations

from datetime import datetime, timezone

import pytest

from app.contracts.bem_payloads import (
    BemConfidenceScore,
    BemSourceMetadata,
    CuratedEvidenceRecord,
    EvidenceKind,
)
from app.services.bem_curated_evidence_adapter import BemCuratedEvidenceAdapter


def _valid_payload() -> dict:
    return {
        "evidence_id": "ev-001",
        "kind": "excel",
        "data": {"sheet": "ventas", "rows": 10},
        "source": {
            "source_name": "upload_owner",
            "source_type": "excel_file",
            "uploaded_at": "2026-05-10T12:00:00+00:00",
            "external_reference_id": "ext-1",
        },
        "confidence": {"score": 0.91, "provider": "bem"},
        "trace_id": "trace-123",
    }


def _adapter() -> BemCuratedEvidenceAdapter:
    return BemCuratedEvidenceAdapter(
        now_provider=lambda: datetime(2026, 5, 10, 15, 0, 0, tzinfo=timezone.utc)
    )


def test_build_curated_evidence_valid_transformation() -> None:
    record = _adapter().build_curated_evidence("tenant-1", _valid_payload())

    assert isinstance(record, CuratedEvidenceRecord)
    assert record.tenant_id == "tenant-1"
    assert record.evidence_id == "ev-001"
    assert record.kind == EvidenceKind.EXCEL
    assert record.payload == {"sheet": "ventas", "rows": 10}
    assert isinstance(record.source_metadata, BemSourceMetadata)
    assert isinstance(record.confidence, BemConfidenceScore)
    assert record.trace_id == "trace-123"
    assert record.received_at == "2026-05-10T15:00:00+00:00"


def test_build_curated_evidence_rejects_empty_tenant() -> None:
    with pytest.raises(ValueError, match="tenant_id"):
        _adapter().build_curated_evidence("", _valid_payload())


def test_build_curated_evidence_rejects_empty_payload() -> None:
    with pytest.raises(ValueError, match="payload"):
        _adapter().build_curated_evidence("tenant-1", {})


def test_build_curated_evidence_rejects_invalid_kind() -> None:
    payload = _valid_payload()
    payload["kind"] = "unsupported"

    with pytest.raises(ValueError, match="kind inválido"):
        _adapter().build_curated_evidence("tenant-1", payload)


def test_build_curated_evidence_rejects_missing_evidence_id() -> None:
    payload = _valid_payload()
    del payload["evidence_id"]

    with pytest.raises(ValueError, match="evidence_id"):
        _adapter().build_curated_evidence("tenant-1", payload)


def test_build_curated_evidence_rejects_invalid_confidence() -> None:
    payload = _valid_payload()
    payload["confidence"] = {"score": 1.5, "provider": "bem"}

    with pytest.raises(ValueError, match="score"):
        _adapter().build_curated_evidence("tenant-1", payload)


def test_build_curated_evidence_rejects_missing_source_metadata() -> None:
    payload = _valid_payload()
    del payload["source"]

    with pytest.raises(ValueError, match="source"):
        _adapter().build_curated_evidence("tenant-1", payload)


def test_build_curated_evidence_trace_id_optional() -> None:
    payload = _valid_payload()
    del payload["trace_id"]

    record = _adapter().build_curated_evidence("tenant-1", payload)
    assert record.trace_id is None


def test_build_curated_evidence_mapping_correct() -> None:
    payload = _valid_payload()
    record = _adapter().build_curated_evidence("tenant-1", payload)

    assert record.evidence_id == payload["evidence_id"]
    assert record.kind.value == payload["kind"]
    assert record.payload == payload["data"]
    assert record.source_metadata.source_name == payload["source"]["source_name"]
    assert record.confidence is not None
    assert record.confidence.score == payload["confidence"]["score"]
    assert record.trace_id == payload["trace_id"]


def test_build_curated_evidence_fail_closed_on_missing_data() -> None:
    payload = _valid_payload()
    del payload["data"]

    with pytest.raises(ValueError, match="data"):
        _adapter().build_curated_evidence("tenant-1", payload)
