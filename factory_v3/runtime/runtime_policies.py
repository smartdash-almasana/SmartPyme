from __future__ import annotations

from enum import Enum
from typing import List

from pydantic import BaseModel, Field

from factory_v3.contracts.entities import AgentCard, TaskEnvelope


class PolicyDecision(str, Enum):
    ALLOW = "allow"
    DENY = "deny"


class PolicyResult(BaseModel):
    decision: PolicyDecision
    reasons: List[str] = Field(default_factory=list)

    @property
    def allowed(self) -> bool:
        return self.decision == PolicyDecision.ALLOW


class RuntimePolicyEngine:
    def evaluate_task_assignment(
        self,
        *,
        task: TaskEnvelope,
        agent: AgentCard,
    ) -> PolicyResult:
        reasons: List[str] = []

        if not task.task_id:
            reasons.append("missing task_id")

        if not task.assigned_agent:
            reasons.append("missing assigned_agent")

        if task.assigned_agent != agent.agent_id:
            reasons.append("task assigned_agent does not match agent_id")

        if not agent.capabilities:
            reasons.append("agent has no declared capabilities")

        if reasons:
            return PolicyResult(decision=PolicyDecision.DENY, reasons=reasons)

        return PolicyResult(decision=PolicyDecision.ALLOW)
