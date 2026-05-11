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


# ---------------------------------------------------------------------------
# Case-insensitive kind parsing
# ---------------------------------------------------------------------------


def test_kind_uppercase_accepted() -> None:
    payload = _valid_payload()
    payload["kind"] = "EXCEL"
    record = _adapter().build_curated_evidence("tenant-1", payload)
    assert record.kind == EvidenceKind.EXCEL


def test_kind_mixed_case_accepted() -> None:
    payload = _valid_payload()
    payload["kind"] = "Excel"
    record = _adapter().build_curated_evidence("tenant-1", payload)
    assert record.kind == EvidenceKind.EXCEL


def test_kind_pdf_uppercase_accepted() -> None:
    payload = _valid_payload()
    payload["kind"] = "PDF"
    record = _adapter().build_curated_evidence("tenant-1", payload)
    assert record.kind == EvidenceKind.PDF


def test_kind_mixed_case_email_accepted() -> None:
    payload = _valid_payload()
    payload["kind"] = "EMAIL"
    record = _adapter().build_curated_evidence("tenant-1", payload)
    assert record.kind == EvidenceKind.EMAIL


def test_kind_invalid_still_rejected() -> None:
    payload = _valid_payload()
    payload["kind"] = "WORD"
    with pytest.raises(ValueError, match="kind inválido"):
        _adapter().build_curated_evidence("tenant-1", payload)


# ===========================================================================
# Tests: build_curated_evidence_from_bem_response
# ===========================================================================


def _bem_response_full() -> dict:
    """Fixture de response_payload real de BEM con todos los campos."""
    return {
        "callReferenceID": "ref-abc-001",
        "callID": "call-xyz-999",
        "avgConfidence": 0.87,
        "inputType": "excel",
        "s3URL": "s3://bucket/ventas.xlsx",
        "workflow_id": "wf-demo-001",
        "outputs": [
            {
                "transformedContent": {
                    "precio_venta": 10.0,
                    "costo_unitario": 80.0,
                    "cantidad": 5,
                    "producto": "Widget A",
                    "source_name": "ventas.xlsx",
                    "source_type": "excel",
                }
            }
        ],
    }


def test_from_bem_response_maps_full_payload() -> None:
    record = _adapter().build_curated_evidence_from_bem_response(
        "tenant-1", _bem_response_full()
    )

    assert isinstance(record, CuratedEvidenceRecord)
    assert record.tenant_id == "tenant-1"
    assert record.evidence_id == "ref-abc-001"
    assert record.kind == EvidenceKind.EXCEL
    assert record.payload["precio_venta"] == 10.0
    assert record.payload["costo_unitario"] == 80.0
    assert record.payload["cantidad"] == 5
    assert record.payload["producto"] == "Widget A"
    assert record.source_metadata.source_name == "ventas.xlsx"
    assert record.source_metadata.source_type == "excel"
    assert record.confidence is not None
    assert record.confidence.score == 0.87
    assert record.confidence.provider == "bem"
    assert record.received_at == "2026-05-10T15:00:00+00:00"


def test_from_bem_response_evidence_id_uses_callReferenceID() -> None:
    payload = _bem_response_full()
    record = _adapter().build_curated_evidence_from_bem_response("tenant-1", payload)
    assert record.evidence_id == "ref-abc-001"


def test_from_bem_response_evidence_id_fallback_to_callID() -> None:
    payload = _bem_response_full()
    del payload["callReferenceID"]
    record = _adapter().build_curated_evidence_from_bem_response("tenant-1", payload)
    assert record.evidence_id == "call-xyz-999"


def test_from_bem_response_evidence_id_fallback_to_run_id() -> None:
    payload = _bem_response_full()
    del payload["callReferenceID"]
    del payload["callID"]
    record = _adapter().build_curated_evidence_from_bem_response(
        "tenant-1", payload, run_id="run-42"
    )
    assert record.evidence_id == "bem-run-run-42"


def test_from_bem_response_fails_if_no_evidence_id_resolvable() -> None:
    payload = _bem_response_full()
    del payload["callReferenceID"]
    del payload["callID"]
    with pytest.raises(ValueError, match="evidence_id"):
        _adapter().build_curated_evidence_from_bem_response("tenant-1", payload)


def test_from_bem_response_fails_if_outputs_empty() -> None:
    payload = _bem_response_full()
    payload["outputs"] = []
    with pytest.raises(ValueError, match="outputs"):
        _adapter().build_curated_evidence_from_bem_response("tenant-1", payload)


def test_from_bem_response_fails_if_outputs_missing() -> None:
    payload = _bem_response_full()
    del payload["outputs"]
    with pytest.raises(ValueError, match="outputs"):
        _adapter().build_curated_evidence_from_bem_response("tenant-1", payload)


def test_from_bem_response_fails_if_transformedContent_missing() -> None:
    payload = _bem_response_full()
    payload["outputs"] = [{"otherField": "x"}]
    with pytest.raises(ValueError, match="transformedContent"):
        _adapter().build_curated_evidence_from_bem_response("tenant-1", payload)


def test_from_bem_response_fails_if_transformedContent_not_dict() -> None:
    payload = _bem_response_full()
    payload["outputs"] = [{"transformedContent": "not-a-dict"}]
    with pytest.raises(ValueError, match="transformedContent"):
        _adapter().build_curated_evidence_from_bem_response("tenant-1", payload)


def test_from_bem_response_confidence_from_avgConfidence() -> None:
    payload = _bem_response_full()
    payload["avgConfidence"] = 0.75
    record = _adapter().build_curated_evidence_from_bem_response("tenant-1", payload)
    assert record.confidence is not None
    assert record.confidence.score == 0.75


def test_from_bem_response_confidence_none_when_absent() -> None:
    payload = _bem_response_full()
    del payload["avgConfidence"]
    record = _adapter().build_curated_evidence_from_bem_response("tenant-1", payload)
    assert record.confidence is None


def test_from_bem_response_source_data_correct() -> None:
    record = _adapter().build_curated_evidence_from_bem_response(
        "tenant-1", _bem_response_full()
    )
    assert record.source_metadata.source_name == "ventas.xlsx"
    assert record.source_metadata.source_type == "excel"


def test_from_bem_response_preserves_bem_meta_in_external_reference_id() -> None:
    import json

    record = _adapter().build_curated_evidence_from_bem_response(
        "tenant-1", _bem_response_full()
    )
    assert record.source_metadata.external_reference_id is not None
    meta = json.loads(record.source_metadata.external_reference_id)
    assert meta["callID"] == "call-xyz-999"
    assert meta["callReferenceID"] == "ref-abc-001"
    assert meta["workflow_id"] == "wf-demo-001"


def test_from_bem_response_fails_on_empty_tenant() -> None:
    with pytest.raises(ValueError, match="tenant_id"):
        _adapter().build_curated_evidence_from_bem_response("", _bem_response_full())


def test_from_bem_response_fails_if_response_payload_not_dict() -> None:
    with pytest.raises(TypeError, match="response_payload"):
        _adapter().build_curated_evidence_from_bem_response("tenant-1", "not-a-dict")  # type: ignore[arg-type]


def test_from_bem_response_data_fallback_to_full_transformedContent_when_no_known_fields() -> None:
    payload = _bem_response_full()
    payload["outputs"] = [
        {"transformedContent": {"custom_field": "valor", "otro": 42}}
    ]
    record = _adapter().build_curated_evidence_from_bem_response("tenant-1", payload)
    assert record.payload == {"custom_field": "valor", "otro": 42}


def test_from_bem_response_kind_inferred_from_inputType() -> None:
    payload = _bem_response_full()
    payload["inputType"] = "pdf"
    payload["outputs"] = [
        {"transformedContent": {"precio_venta": 5, "source_type": "pdf"}}
    ]
    record = _adapter().build_curated_evidence_from_bem_response("tenant-1", payload)
    assert record.kind == EvidenceKind.PDF


def test_from_bem_response_kind_defaults_to_mixed_for_unknown_type() -> None:
    payload = _bem_response_full()
    payload["inputType"] = "word"
    payload["outputs"] = [
        {"transformedContent": {"precio_venta": 5}}
    ]
    record = _adapter().build_curated_evidence_from_bem_response("tenant-1", payload)
    assert record.kind == EvidenceKind.MIXED
