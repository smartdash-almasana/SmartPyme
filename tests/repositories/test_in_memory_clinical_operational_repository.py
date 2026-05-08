"""Tests del InMemoryClinicalOperationalRepository.

Verifica aislamiento soberano por tenant_id, upsert semántico,
fail-closed ante IDs vacíos y filtrado correcto por reception.

Sin DB, sin red, sin dependencias externas.
"""

from __future__ import annotations

import pytest

from app.contracts.clinical_operational_contracts import (
    EvidenceRecord,
    ReceptionRecord,
)
from app.repositories.in_memory_clinical_operational_repository import (
    InMemoryClinicalOperationalRepository,
)


# ---------------------------------------------------------------------------
# Helpers de fixtures mínimos
# ---------------------------------------------------------------------------

def _make_reception(
    tenant_id: str = "tenant_a",
    reception_id: str = "rec_001",
    original_message: str = "no me cierra la caja",
    status: str = "RECEIVED",
    **kwargs,
) -> ReceptionRecord:
    return ReceptionRecord(
        reception_id=reception_id,
        tenant_id=tenant_id,
        channel="telegram",
        original_message=original_message,
        status=status,
        **kwargs,
    )


def _make_evidence(
    tenant_id: str = "tenant_a",
    evidence_id: str = "ev_001",
    status: str = "RECEIVED",
    linked_reception_id: str | None = None,
    source_type: str = "excel",
    **kwargs,
) -> EvidenceRecord:
    return EvidenceRecord(
        evidence_id=evidence_id,
        tenant_id=tenant_id,
        source_type=source_type,
        status=status,
        linked_reception_id=linked_reception_id,
        **kwargs,
    )


def _repo() -> InMemoryClinicalOperationalRepository:
    return InMemoryClinicalOperationalRepository()


# ===========================================================================
# ReceptionRecord — tests
# ===========================================================================

def test_guarda_y_recupera_reception():
    repo = _repo()
    rec = _make_reception()
    repo.save_reception(rec)

    resultado = repo.get_reception("tenant_a", "rec_001")

    assert resultado is not None
    assert resultado.reception_id == "rec_001"
    assert resultado.tenant_id == "tenant_a"


def test_upsert_reception_pisa_registro_previo():
    repo = _repo()
    rec_v1 = _make_reception(original_message="versión 1")
    rec_v2 = _make_reception(original_message="versión 2")

    repo.save_reception(rec_v1)
    repo.save_reception(rec_v2)

    resultado = repo.get_reception("tenant_a", "rec_001")
    assert resultado is not None
    assert resultado.original_message == "versión 2"


def test_no_permite_leer_reception_de_otro_tenant():
    repo = _repo()
    rec = _make_reception(tenant_id="tenant_a", reception_id="rec_001")
    repo.save_reception(rec)

    resultado = repo.get_reception("tenant_b", "rec_001")

    assert resultado is None


def test_list_receptions_filtra_por_tenant():
    repo = _repo()
    repo.save_reception(_make_reception(tenant_id="tenant_a", reception_id="rec_001"))
    repo.save_reception(_make_reception(tenant_id="tenant_a", reception_id="rec_002"))
    repo.save_reception(_make_reception(tenant_id="tenant_b", reception_id="rec_003"))

    resultado = repo.list_receptions("tenant_a")

    assert len(resultado) == 2
    ids = {r.reception_id for r in resultado}
    assert ids == {"rec_001", "rec_002"}


def test_list_receptions_tenant_sin_registros_devuelve_lista_vacia():
    repo = _repo()

    resultado = repo.list_receptions("tenant_sin_datos")

    assert resultado == []


def test_tenant_id_vacio_falla_en_save_reception():
    repo = _repo()
    with pytest.raises((ValueError, Exception)):
        # El contrato Pydantic ya rechaza tenant_id vacío
        _make_reception(tenant_id="")


def test_tenant_id_espacios_falla_en_get_reception():
    repo = _repo()
    with pytest.raises(ValueError):
        repo.get_reception("   ", "rec_001")


def test_tenant_id_espacios_falla_en_list_receptions():
    repo = _repo()
    with pytest.raises(ValueError):
        repo.list_receptions("   ")


def test_reception_id_vacio_falla_en_get_reception():
    repo = _repo()
    with pytest.raises(ValueError):
        repo.get_reception("tenant_a", "")


def test_reception_id_espacios_falla_en_get_reception():
    repo = _repo()
    with pytest.raises(ValueError):
        repo.get_reception("tenant_a", "   ")


# ===========================================================================
# EvidenceRecord — tests
# ===========================================================================

def test_guarda_y_recupera_evidence():
    repo = _repo()
    ev = _make_evidence()
    repo.save_evidence(ev)

    resultado = repo.get_evidence("tenant_a", "ev_001")

    assert resultado is not None
    assert resultado.evidence_id == "ev_001"
    assert resultado.tenant_id == "tenant_a"


def test_upsert_evidence_pisa_registro_previo():
    repo = _repo()
    ev_v1 = _make_evidence(source_type="excel")
    ev_v2 = _make_evidence(source_type="pdf")

    repo.save_evidence(ev_v1)
    repo.save_evidence(ev_v2)

    resultado = repo.get_evidence("tenant_a", "ev_001")
    assert resultado is not None
    assert resultado.source_type == "pdf"


def test_no_permite_leer_evidence_de_otro_tenant():
    repo = _repo()
    ev = _make_evidence(tenant_id="tenant_a", evidence_id="ev_001")
    repo.save_evidence(ev)

    resultado = repo.get_evidence("tenant_b", "ev_001")

    assert resultado is None


def test_list_evidence_filtra_por_tenant():
    repo = _repo()
    repo.save_evidence(_make_evidence(tenant_id="tenant_a", evidence_id="ev_001"))
    repo.save_evidence(_make_evidence(tenant_id="tenant_a", evidence_id="ev_002"))
    repo.save_evidence(_make_evidence(tenant_id="tenant_b", evidence_id="ev_003"))

    resultado = repo.list_evidence("tenant_a")

    assert len(resultado) == 2
    ids = {e.evidence_id for e in resultado}
    assert ids == {"ev_001", "ev_002"}


def test_list_evidence_for_reception_devuelve_solo_vinculadas():
    repo = _repo()
    ev_vinculada = _make_evidence(
        evidence_id="ev_001",
        status="LINKED",
        linked_reception_id="rec_001",
    )
    ev_otra_reception = _make_evidence(
        evidence_id="ev_002",
        status="LINKED",
        linked_reception_id="rec_002",
    )
    ev_sin_vincular = _make_evidence(
        evidence_id="ev_003",
        status="RECEIVED",
    )

    repo.save_evidence(ev_vinculada)
    repo.save_evidence(ev_otra_reception)
    repo.save_evidence(ev_sin_vincular)

    resultado = repo.list_evidence_for_reception("tenant_a", "rec_001")

    assert len(resultado) == 1
    assert resultado[0].evidence_id == "ev_001"


def test_list_evidence_for_reception_sin_vinculadas_devuelve_vacia():
    repo = _repo()
    repo.save_evidence(_make_evidence(evidence_id="ev_001", status="RECEIVED"))

    resultado = repo.list_evidence_for_reception("tenant_a", "rec_999")

    assert resultado == []


def test_list_evidence_tenant_sin_registros_devuelve_lista_vacia():
    repo = _repo()

    resultado = repo.list_evidence("tenant_sin_datos")

    assert resultado == []


def test_tenant_id_vacio_falla_en_save_evidence():
    repo = _repo()
    with pytest.raises((ValueError, Exception)):
        _make_evidence(tenant_id="")


def test_tenant_id_espacios_falla_en_get_evidence():
    repo = _repo()
    with pytest.raises(ValueError):
        repo.get_evidence("   ", "ev_001")


def test_tenant_id_espacios_falla_en_list_evidence():
    repo = _repo()
    with pytest.raises(ValueError):
        repo.list_evidence("   ")


def test_tenant_id_espacios_falla_en_list_evidence_for_reception():
    repo = _repo()
    with pytest.raises(ValueError):
        repo.list_evidence_for_reception("   ", "rec_001")


def test_evidence_id_vacio_falla_en_get_evidence():
    repo = _repo()
    with pytest.raises(ValueError):
        repo.get_evidence("tenant_a", "")


def test_evidence_id_espacios_falla_en_get_evidence():
    repo = _repo()
    with pytest.raises(ValueError):
        repo.get_evidence("tenant_a", "   ")


# ===========================================================================
# Aislamiento cruzado tenant_a / tenant_b
# ===========================================================================

def test_aislamiento_completo_entre_tenants():
    repo = _repo()

    repo.save_reception(_make_reception(tenant_id="tenant_a", reception_id="rec_001"))
    repo.save_evidence(_make_evidence(tenant_id="tenant_a", evidence_id="ev_001"))

    assert repo.get_reception("tenant_b", "rec_001") is None
    assert repo.get_evidence("tenant_b", "ev_001") is None
    assert repo.list_receptions("tenant_b") == []
    assert repo.list_evidence("tenant_b") == []
