from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ApprovalRequest:
    task_id: str
    requester_agent: str
    reason: str


@dataclass
class ApprovalResult:
    approved: bool
    reason: str


class HermesApprovalBridge:
    def request_approval(self, request: ApprovalRequest) -> ApprovalResult:
        return ApprovalResult(
            approved=False,
            reason="Hermes approval bridge not connected",
        )
