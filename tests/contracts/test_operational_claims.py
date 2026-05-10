import pytest

from app.contracts.operational_claims import (
    CLAIM_CATALOG,
    ClaimEstado,
    ClaimType,
    OperationalClaim,
    puede_marcar_supported,
    resolver_estado_fail_closed,
    transicion_valida,
)


def test_claim_type_has_expected_values():
    assert {item.value for item in ClaimType} == {
        "deuda_cobranza",
        "stock",
        "ventas",
        "costos",
        "margen",
        "proveedor",
        "cliente",
        "facturacion",
    }


def test_claim_estado_has_expected_values():
    assert {item.value for item in ClaimEstado} == {
        "pending_confirmation",
        "confirmed",
        "rejected",
        "evidence_requested",
        "evidence_received",
        "supported",
        "blocked",
    }


def test_claim_catalog_covers_all_claim_types():
    assert set(CLAIM_CATALOG.keys()) == set(ClaimType)
    for entry in CLAIM_CATALOG.values():
        assert entry.significado_operacional
        assert len(entry.datos_minimos) >= 2
        assert len(entry.evidencia_esperada) >= 2
        assert entry.pregunta_confirmacion
        assert entry.pregunta_evidencia


def test_operational_claim_rejects_empty_tenant_id():
    with pytest.raises(ValueError, match="tenant_id"):
        OperationalClaim(
            tenant_id="",
            session_id="session-1",
            source_turn_id="turn-1",
            claim_type=ClaimType.STOCK,
            statement="Hay un problema de stock.",
        )


def test_operational_claim_to_dict_serializes_enums_as_strings():
    claim = OperationalClaim(
        tenant_id="tenant-1",
        session_id="session-1",
        source_turn_id="turn-1",
        claim_type=ClaimType.DEUDA_COBRANZA,
        statement="Cliente con deuda pendiente.",
    )

    data = claim.to_dict()

    assert data["claim_type"] == "deuda_cobranza"
    assert data["status"] == "pending_confirmation"
    assert data["evidence_ids"] == []


def test_valid_transition_confirmed_to_evidence_requested():
    assert transicion_valida(
        ClaimEstado.CONFIRMED,
        ClaimEstado.EVIDENCE_REQUESTED,
    )


def test_invalid_transition_resolves_to_blocked():
    assert (
        resolver_estado_fail_closed(
            ClaimEstado.CONFIRMED,
            ClaimEstado.SUPPORTED,
        )
        == ClaimEstado.BLOCKED
    )


def test_puede_marcar_supported_requires_evidence_ids():
    without_evidence = OperationalClaim(
        tenant_id="tenant-1",
        session_id="session-1",
        source_turn_id="turn-1",
        claim_type=ClaimType.STOCK,
        statement="Diferencia de stock.",
        status=ClaimEstado.EVIDENCE_RECEIVED,
    )
    with_evidence = OperationalClaim(
        tenant_id="tenant-1",
        session_id="session-1",
        source_turn_id="turn-1",
        claim_type=ClaimType.STOCK,
        statement="Diferencia de stock.",
        status=ClaimEstado.EVIDENCE_RECEIVED,
        evidence_ids=("ev-1",),
    )

    assert puede_marcar_supported(without_evidence) is False
    assert puede_marcar_supported(with_evidence) is True