import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.core.clarification.models import ClarificationRequest
from app.core.clarification.persistence import init_clarifications_db
from app.core.clarification.service import (
    create_clarification,
    get_pending_clarifications,
    has_blocking_pending,
    resolve_existing_clarification,
)


@pytest.fixture(autouse=True)
def isolated_clarifications_db(tmp_path, monkeypatch):
    db_path = tmp_path / "clarifications.db"
    monkeypatch.setenv("SMARTPYME_CLARIFICATIONS_DB", str(db_path))
    yield


def test_save_clarification_and_list_pending():
    request = ClarificationRequest(
        clarification_id="c-001",
        entity_type="proveedor",
        value_a="ACME SA",
        value_b="ACME S.A.",
        reason="Nombre similar con distinta puntuacion",
        blocking=True,
    )
    create_clarification(request=request)

    pending = get_pending_clarifications()

    assert len(pending) == 1
    assert pending[0].clarification_id == "c-001"
    assert pending[0].status == "pending"


def test_resolve_clarification_successfully():
    create_clarification(
        clarification_id="c-002",
        entity_type="cliente",
        value_a="12345678",
        value_b="12345679",
        reason="CUIT potencialmente inconsistente",
        blocking=True,
    )

    resolved = resolve_existing_clarification("c-002", "Tomar value_a como canonico")

    assert resolved is True


def test_resolved_clarification_no_longer_appears_in_pending_list():
    create_clarification(
        clarification_id="c-003",
        entity_type="producto",
        value_a="COD-01",
        value_b="COD-001",
        reason="Codigo potencialmente duplicado",
        blocking=False,
    )
    resolve_existing_clarification("c-003", "Usar COD-001")

    pending = get_pending_clarifications()

    assert pending == []


def test_duplicate_clarification_id_is_rejected():
    create_clarification(
        clarification_id="c-004",
        entity_type="proveedor",
        value_a="A",
        value_b="B",
        reason="Duplicado intencional",
        blocking=True,
    )

    with pytest.raises(ValueError, match="CLARIFICATION_ID_DUPLICADO"):
        create_clarification(
            clarification_id="c-004",
            entity_type="proveedor",
            value_a="A2",
            value_b="B2",
            reason="Duplicado intencional 2",
            blocking=True,
        )


def test_empty_resolution_is_rejected():
    create_clarification(
        clarification_id="c-005",
        entity_type="cliente",
        value_a="valor1",
        value_b="valor2",
        reason="Se requiere decision humana",
        blocking=True,
    )

    with pytest.raises(ValueError, match="RESOLUTION_INVALIDA"):
        resolve_existing_clarification("c-005", "   ")


def test_persistence_initializes_cleanly():
    init_clarifications_db()

    pending = get_pending_clarifications()

    assert pending == []


def test_fail_closed_cycle_blocks_and_unblocks_after_resolution():
    assert has_blocking_pending() is False

    create_clarification(
        clarification_id="c-006",
        entity_type="cliente",
        value_a="20-11111111-1",
        value_b="20-11111111-2",
        reason="CUIT con ambiguedad",
        blocking=True,
    )

    assert has_blocking_pending() is True

    resolved = resolve_existing_clarification("c-006", "Confirmar value_a")
    assert resolved is True
    assert has_blocking_pending() is False
