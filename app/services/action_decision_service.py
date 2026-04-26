from __future__ import annotations

from dataclasses import replace
from typing import Any

from app.contracts.action_contract import ActionProposal


class InvalidDecisionError(Exception):
    """Raised when an approve/reject is attempted on an already-executed proposal."""


class ActionDecisionService:
    """
    Approves or rejects ActionProposal objects.
    Returns a NEW ActionProposal with the updated status.
    Does NOT execute any action. Does NOT call external services.
    """

    def approve(self, proposal: ActionProposal) -> ActionProposal:
        """
        Returns a new ActionProposal with status='approved'.
        Raises InvalidDecisionError if the proposal is already executed.
        """
        if proposal.status == "executed":
            raise InvalidDecisionError(
                f"Cannot approve proposal '{proposal.action_id}': already executed."
            )
        return replace(proposal, status="approved")

    def reject(
        self,
        proposal: ActionProposal,
        reason: str | None = None,
    ) -> ActionProposal:
        """
        Returns a new ActionProposal with status='rejected'.
        If reason is provided it is appended to traceable_origin under 'rejection_reason'.
        Raises InvalidDecisionError if the proposal is already executed.
        """
        if proposal.status == "executed":
            raise InvalidDecisionError(
                f"Cannot reject proposal '{proposal.action_id}': already executed."
            )
        updated_origin: dict[str, Any] = dict(proposal.traceable_origin)
        if reason is not None:
            updated_origin["rejection_reason"] = reason
        return replace(proposal, status="rejected", traceable_origin=updated_origin)
