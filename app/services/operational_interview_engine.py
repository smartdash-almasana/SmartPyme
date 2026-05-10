from __future__ import annotations

from app.contracts.operational_claims import ClaimEstado, OperationalClaim
from app.services.mock_claim_extractor import MockClaimExtractor


class OperationalInterviewEngine:
    """Offline engine: intake message -> extracted claims -> OperationalClaim objects."""

    def __init__(self, extractor: MockClaimExtractor | None = None) -> None:
        self.extractor = extractor or MockClaimExtractor()

    def process_turn(
        self,
        *,
        tenant_id: str,
        session_id: str,
        source_turn_id: str,
        message: str,
    ) -> list[OperationalClaim]:
        extracted = self.extractor.extract(message)
        claims: list[OperationalClaim] = []
        for claim_type, statement in extracted:
            claims.append(
                OperationalClaim(
                    tenant_id=tenant_id,
                    session_id=session_id,
                    source_turn_id=source_turn_id,
                    claim_type=claim_type,
                    statement=statement,
                    status=ClaimEstado.PENDING_CONFIRMATION,
                )
            )
        return claims
