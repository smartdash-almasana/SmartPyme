import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.core.clarification.service import (
    create_clarification,
    has_blocking_pending,
    list_pending,
    resolve_clarification,
)


@pytest.fixture(autouse=True)
def isolated_clarifications_db(tmp_path, monkeypatch):
    db_path = tmp_path / "clarifications.db"
    monkeypatch.setenv("SMARTPYME_CLARIFICATIONS_DB", str(db_path))
    yield


def test_create_clarification_creates_record_correctly():
    created = create_clarification(
        clarification_id="clar-001",
        entity_type="cliente",
        value_a="20-12345678-9",
        value_b="20123456789",
        reason="Formato de CUIT inconsistente",
        blocking=True,
    )

    assert created.clarification_id == "clar-001"
    assert created.status == "pending"
    assert created.blocking is True
    assert created.resolution is None


def test_list_pending_returns_only_unresolved_records():
    create_clarification(
        clarification_id="clar-002",
        entity_type="proveedor",
        value_a="ACME SA",
        value_b="ACME S.A.",
        reason="Nombre potencialmente duplicado",
        blocking=False,
    )
    create_clarification(
        clarification_id="clar-003",
        entity_type="producto",
        value_a="SKU-100",
        value_b="SKU100",
        reason="Codificacion con separador ambiguo",
        blocking=True,
    )
    resolve_clarification("clar-003", "Usar SKU-100 como canonico")

    pending = list_pending()

    assert len(pending) == 1
    assert pending[0].clarification_id == "clar-002"


def test_resolve_clarification_changes_status_correctly():
    create_clarification(
        clarification_id="clar-004",
        entity_type="cuenta",
        value_a="CTA-1",
        value_b="CTA-01",
        reason="Cuenta duplicada",
        blocking=False,
    )

    resolved = resolve_clarification("clar-004", "Conservar CTA-01")
    pending = list_pending()

    assert resolved is True
    assert pending == []


def test_has_blocking_pending_returns_true_when_unresolved_blocking_exists():
    create_clarification(
        clarification_id="clar-005",
        entity_type="cliente",
        value_a="A",
        value_b="B",
        reason="Se requiere decision humana",
        blocking=True,
    )

    assert has_blocking_pending() is True


def test_has_blocking_pending_returns_false_when_all_blocking_are_resolved():
    create_clarification(
        clarification_id="clar-006",
        entity_type="cliente",
        value_a="X",
        value_b="Y",
        reason="Decision pendiente",
        blocking=True,
    )
    resolve_clarification("clar-006", "Resolver con X")

    assert has_blocking_pending() is False
