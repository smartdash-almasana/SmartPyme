from __future__ import annotations

import asyncio
import uuid

from factory_prefect.contracts.hitl import HumanApprovalRequest, HumanApprovalResult


class HermesApprovalClient:
    """Fail-closed Hermes HITL boundary.

    V1 intentionally does not execute network calls. If no endpoint is configured,
    approval fails closed and the caller must block the workflow.
    """

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
                raw_message=None,
                normalized_answer={
                    "reason": "Hermes endpoint is not configured yet.",
                    "run_id": request.run_id,
                    "task_id": request.task_id,
                    "risk_type": request.risk_type,
                },
            )

        await asyncio.sleep(0)
        return HumanApprovalResult(
            ticket_id=f"hitl_{uuid.uuid4().hex}",
            status="FAILED",
            approved=False,
            decision_type="FAILED",
            raw_message=None,
            normalized_answer={
                "reason": "Hermes HTTP integration is intentionally not implemented in HITO_002.",
                "endpoint": self.endpoint,
                "run_id": request.run_id,
                "task_id": request.task_id,
            },
        )
