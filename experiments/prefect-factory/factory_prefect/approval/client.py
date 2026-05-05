from __future__ import annotations

import asyncio
import uuid

from factory_prefect.contracts.hitl import HumanApprovalRequest, HumanApprovalResult


class ApprovalClient:
    def __init__(self, endpoint: str | None = None) -> None:
        self.endpoint = endpoint

    async def request_approval(self, request: HumanApprovalRequest) -> HumanApprovalResult:
        if self.endpoint is None:
            await asyncio.sleep(0)
            return HumanApprovalResult(
                ticket_id=f"hitl_{uuid.uuid4().hex}",
                status="FAILED",
                approved=False,
                decision_type="FAILED",
                normalized_answer={
                    "reason": "approval endpoint is not configured"
                },
            )

        raise NotImplementedError("HTTP approval gateway integration is not implemented in HITO_002")
