from __future__ import annotations

from app.contracts.operational_claims import ClaimEstado, ClaimType
from app.services.operational_interview_engine import OperationalInterviewEngine


def test_operational_interview_engine_offline_end_to_end() -> None:
    engine = OperationalInterviewEngine()

    claims = engine.process_turn(
        tenant_id="tenant-1",
        session_id="session-1",
        source_turn_id="turn-1",
        message="Tengo deuda de clientes y problemas de stock esta semana.",
    )

    assert len(claims) >= 2
    assert {claim.claim_type for claim in claims} >= {ClaimType.DEUDA_COBRANZA, ClaimType.STOCK}

    for claim in claims:
        assert claim.tenant_id == "tenant-1"
        assert claim.session_id == "session-1"
        assert claim.source_turn_id == "turn-1"
        assert claim.status == ClaimEstado.PENDING_CONFIRMATION
        assert claim.evidence_ids == ()
