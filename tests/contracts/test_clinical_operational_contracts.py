from __future__ import annotations

from datetime import datetime

import pytest
from pydantic import ValidationError

from app.contracts.clinical_operational_contracts import (
    EvidenceRecord,
    ReceptionRecord,
)


def _valid_reception(**overrides):
    payload = {
        "reception_id": "rec_001",
        "tenant_id": "tenant_demo",
        "channel": "whatsapp",
        "original_message": "Vendo mucho pero no queda plata",
        "expressed_pain": "problema de caja",
        "initial_classification": "margen_erosionado",
        "status": "RECEIVED",
        "requested_evidence_ids": [],
        "received_evidence_ids": [],
        "result_id": None,
        "blocking_reason": None,
        "detected_opportunity": None,
        "created_at": datetime.utcnow(),
    }
    payload.update(overrides)
    return ReceptionRecord(**payload)


def _valid_evidence(**overrides):
    payload = {
        "evidence_id": "ev_001",
        "tenant_id": "tenant_demo",
        "source_type": "excel",
        "source_name": "stock_mayo.xlsx",
        "received_from": "paulita",
        "storage_ref": "s3://bucket/file.xlsx",
        "content_hash": "abc123",
        "status": "RECEIVED",
        "linked_reception_id": None,
        "quality_flags": [],
        "created_at": datetime.utcnow(),
    }
    payload.update(overrides)
    return EvidenceRecord(**payload)


def test_crea_reception_record_valido():
    rec = _valid_reception()

    assert rec.tenant_id == "tenant_demo"
    assert rec.status == "RECEIVED"


def test_reception_rechaza_tenant_id_vacio():
    with pytest.raises(ValidationError, match="tenant_id"):
        _valid_reception(tenant_id="   ")


def test_reception_rechaza_original_message_vacio():
    with pytest.raises(ValidationError, match="original_message"):
        _valid_reception(original_message="")


def test_reception_blocked_requiere_blocking_reason():
    with pytest.raises(ValidationError, match="blocking_reason"):
        _valid_reception(status="BLOCKED", blocking_reason=None)


def test_reception_needs_evidence_requiere_requested_evidence_ids():
    with pytest.raises(ValidationError, match="requested_evidence_ids"):
        _valid_reception(status="NEEDS_EVIDENCE", requested_evidence_ids=[])


def test_crea_evidence_record_valido():
    ev = _valid_evidence()

    assert ev.evidence_id == "ev_001"
    assert ev.status == "RECEIVED"


def test_evidence_linked_requiere_linked_reception_id():
    with pytest.raises(ValidationError, match="linked_reception_id"):
        _valid_evidence(status="LINKED", linked_reception_id=None)


def test_evidence_rejected_requiere_quality_flags():
    with pytest.raises(ValidationError, match="quality_flags"):
        _valid_evidence(status="REJECTED", quality_flags=[])


def test_source_type_rechaza_valor_fuera_de_literal():
    with pytest.raises(ValidationError):
        _valid_evidence(source_type="audio")  # type: ignore[arg-type]


def test_status_rechaza_valor_fuera_de_literal():
    with pytest.raises(ValidationError):
        _valid_reception(status="DIAGNOSTIC_CONFIRMED")  # type: ignore[arg-type]



def test_contratos_no_tienen_campos_de_diagnostico_ni_hallazgo_final():
    reception_fields = set(ReceptionRecord.model_fields.keys())
    evidence_fields = set(EvidenceRecord.model_fields.keys())

    forbidden_fields = {
        "diagnostico_final",
        "diagnostico_emitido",
        "finding_record",
        "hallazgo_final",
        "hallazgo_confirmado",
    }

    assert forbidden_fields.isdisjoint(reception_fields)
    assert forbidden_fields.isdisjoint(evidence_fields)
