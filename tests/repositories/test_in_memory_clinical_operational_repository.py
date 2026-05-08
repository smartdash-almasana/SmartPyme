from __future__ import annotations

from datetime import UTC, datetime

import pytest

from app.contracts.clinical_operational_contracts import EvidenceRecord, ReceptionRecord
from app.repositories.in_memory_clinical_operational_repository import (
    InMemoryClinicalOperationalRepository,
)


def _reception(tenant_id: str, reception_id: str, **overrides) -> ReceptionRecord:
    payload = {
        "reception_id": reception_id,
        "tenant_id": tenant_id,
        "channel": "whatsapp",
        "original_message": "Tengo problemas de caja",
        "expressed_pain": "caja",
        "initial_classification": "caja_inconsistente",
        "status": "RECEIVED",
        "requested_evidence_ids": [],
        "received_evidence_ids": [],
        "result_id": None,
        "blocking_reason": None,
        "detected_opportunity": None,
        "created_at": datetime.now(UTC),
    }
    payload.update(overrides)
    return ReceptionRecord(**payload)


def _evidence(tenant_id: str, evidence_id: str, **overrides) -> EvidenceRecord:
    payload = {
        "evidence_id": evidence_id,
        "tenant_id": tenant_id,
        "source_type": "excel",
        "source_name": "estado_resultados.xlsx",
        "received_from": "dueno",
        "storage_ref": "mem://estado_resultados.xlsx",
        "content_hash": "hash-001",
        "status": "RECEIVED",
        "linked_reception_id": None,
        "quality_flags": [],
        "created_at": datetime.now(UTC),
    }
    payload.update(overrides)
    return EvidenceRecord(**payload)


def test_guarda_y_recupera_reception_record():
    repo = InMemoryClinicalOperationalRepository()
    record = _reception("tenant_a", "rec_1")

    repo.save_reception(record)
    loaded = repo.get_reception("tenant_a", "rec_1")

    assert loaded is not None
    assert loaded.reception_id == "rec_1"
    assert loaded.tenant_id == "tenant_a"


def test_upsert_reception_record_pisa_registro_previo_mismo_tenant_id():
    repo = InMemoryClinicalOperationalRepository()
    first = _reception("tenant_a", "rec_1", original_message="mensaje inicial")
    second = _reception("tenant_a", "rec_1", original_message="mensaje actualizado")

    repo.save_reception(first)
    repo.save_reception(second)
    loaded = repo.get_reception("tenant_a", "rec_1")

    assert loaded is not None
    assert loaded.original_message == "mensaje actualizado"


def test_no_permite_leer_reception_record_de_otro_tenant():
    repo = InMemoryClinicalOperationalRepository()
    repo.save_reception(_reception("tenant_a", "rec_1"))

    loaded = repo.get_reception("tenant_b", "rec_1")

    assert loaded is None


def test_list_receptions_filtra_por_tenant():
    repo = InMemoryClinicalOperationalRepository()
    repo.save_reception(_reception("tenant_a", "rec_1"))
    repo.save_reception(_reception("tenant_a", "rec_2"))
    repo.save_reception(_reception("tenant_b", "rec_1"))

    records = repo.list_receptions("tenant_a")

    assert len(records) == 2
    assert {record.reception_id for record in records} == {"rec_1", "rec_2"}
    assert all(record.tenant_id == "tenant_a" for record in records)


def test_reception_tenant_id_vacio_falla_en_save_get_list():
    repo = InMemoryClinicalOperationalRepository()

    with pytest.raises(ValueError, match="tenant_id"):
        repo.save_reception(_reception(" ", "rec_1"))

    with pytest.raises(ValueError, match="tenant_id"):
        repo.get_reception("", "rec_1")

    with pytest.raises(ValueError, match="tenant_id"):
        repo.list_receptions("   ")


def test_get_reception_con_reception_id_vacio_falla():
    repo = InMemoryClinicalOperationalRepository()

    with pytest.raises(ValueError, match="reception_id"):
        repo.get_reception("tenant_a", " ")


def test_guarda_y_recupera_evidence_record():
    repo = InMemoryClinicalOperationalRepository()
    record = _evidence("tenant_a", "ev_1")

    repo.save_evidence(record)
    loaded = repo.get_evidence("tenant_a", "ev_1")

    assert loaded is not None
    assert loaded.evidence_id == "ev_1"
    assert loaded.tenant_id == "tenant_a"


def test_upsert_evidence_record_pisa_registro_previo_mismo_tenant_id():
    repo = InMemoryClinicalOperationalRepository()
    first = _evidence("tenant_a", "ev_1", source_name="archivo_v1.xlsx")
    second = _evidence("tenant_a", "ev_1", source_name="archivo_v2.xlsx")

    repo.save_evidence(first)
    repo.save_evidence(second)
    loaded = repo.get_evidence("tenant_a", "ev_1")

    assert loaded is not None
    assert loaded.source_name == "archivo_v2.xlsx"


def test_no_permite_leer_evidence_record_de_otro_tenant():
    repo = InMemoryClinicalOperationalRepository()
    repo.save_evidence(_evidence("tenant_a", "ev_1"))

    loaded = repo.get_evidence("tenant_b", "ev_1")

    assert loaded is None


def test_list_evidence_filtra_por_tenant():
    repo = InMemoryClinicalOperationalRepository()
    repo.save_evidence(_evidence("tenant_a", "ev_1"))
    repo.save_evidence(_evidence("tenant_a", "ev_2"))
    repo.save_evidence(_evidence("tenant_b", "ev_1"))

    records = repo.list_evidence("tenant_a")

    assert len(records) == 2
    assert {record.evidence_id for record in records} == {"ev_1", "ev_2"}
    assert all(record.tenant_id == "tenant_a" for record in records)


def test_list_evidence_for_reception_devuelve_solo_las_vinculadas():
    repo = InMemoryClinicalOperationalRepository()
    repo.save_evidence(_evidence("tenant_a", "ev_1", linked_reception_id="rec_1", status="LINKED"))
    repo.save_evidence(_evidence("tenant_a", "ev_2", linked_reception_id="rec_2", status="LINKED"))
    repo.save_evidence(_evidence("tenant_a", "ev_3", linked_reception_id=None))
    repo.save_evidence(_evidence("tenant_b", "ev_4", linked_reception_id="rec_1", status="LINKED"))

    records = repo.list_evidence_for_reception("tenant_a", "rec_1")

    assert len(records) == 1
    assert records[0].evidence_id == "ev_1"


def test_evidence_tenant_id_vacio_falla_en_save_get_list():
    repo = InMemoryClinicalOperationalRepository()

    with pytest.raises(ValueError, match="tenant_id"):
        repo.save_evidence(_evidence(" ", "ev_1"))

    with pytest.raises(ValueError, match="tenant_id"):
        repo.get_evidence("", "ev_1")

    with pytest.raises(ValueError, match="tenant_id"):
        repo.list_evidence("   ")


def test_get_evidence_con_evidence_id_vacio_falla():
    repo = InMemoryClinicalOperationalRepository()

    with pytest.raises(ValueError, match="evidence_id"):
        repo.get_evidence("tenant_a", " ")
