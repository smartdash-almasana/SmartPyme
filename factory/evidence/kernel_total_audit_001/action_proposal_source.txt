from __future__ import annotations

import hashlib
from typing import Any

from app.contracts.action_contract import ActionProposal
from app.contracts.communication_contract import FindingMessage
from app.services.findings_service import Finding

# Severity → whether the proposal requires human confirmation before execution.
_REQUIRES_CONFIRMATION: dict[str, bool] = {
    "CRITICO": True,
    "ALTO":    True,
    "MEDIO":   True,
    "BAJO":    False,
    "INFO":    False,
}


class ActionProposalService:
    """
    Generates ActionProposal objects from findings or messages.
    Does NOT execute any action. Does NOT call external services.
    All proposals start with status='proposed'.
    """

    def propose_from_finding(self, finding: Finding) -> ActionProposal:
        action_id = _build_action_id(finding.finding_id, "finding")
        requires_confirmation = _REQUIRES_CONFIRMATION.get(finding.severity, True)

        title = (
            f"Acción propuesta: {finding.suggested_action} "
            f"[{finding.severity}] en {finding.entity_type}/{finding.metric}"
        )
        description = (
            f"Diferencia detectada en '{finding.metric}' entre "
            f"'{finding.entity_id_a}' y '{finding.entity_id_b}': "
            f"{finding.source_a_value} vs {finding.source_b_value} "
            f"(Δ {finding.difference:+.2f}, {finding.difference_pct:+.1f}%)."
        )

        return ActionProposal(
            action_id=action_id,
            source_id=finding.finding_id,
            source_type="finding",
            title=title,
            description=description,
            recommended_action=finding.suggested_action,
            status="proposed",
            requires_confirmation=requires_confirmation,
            traceable_origin=finding.traceable_origin,
        )

    def propose_from_message(self, message: FindingMessage) -> ActionProposal:
        action_id = _build_action_id(message.message_id, "message")
        requires_confirmation = _REQUIRES_CONFIRMATION.get(message.severity, True)

        return ActionProposal(
            action_id=action_id,
            source_id=message.message_id,
            source_type="message",
            title=message.title,
            description=message.body,
            recommended_action=message.action_text,
            status="proposed",
            requires_confirmation=requires_confirmation,
            traceable_origin=message.traceable_origin,
        )

    def propose_batch_from_messages(
        self, messages: list[FindingMessage]
    ) -> list[ActionProposal]:
        return [self.propose_from_message(m) for m in messages]


def _build_action_id(source_id: str, source_type: str) -> str:
    digest = hashlib.sha256(f"{source_type}:{source_id}".encode()).hexdigest()
    return f"action_{digest[:16]}"
