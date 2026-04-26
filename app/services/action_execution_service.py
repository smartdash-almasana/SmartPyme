from __future__ import annotations

from dataclasses import replace

from app.contracts.action_contract import ActionProposal


class NotApprovedError(Exception):
    """Raised when execute() is called on a proposal that is not approved."""


class ActionExecutionService:
    """
    Marks an approved ActionProposal as executed.
    Returns a NEW ActionProposal with status='executed'.
    Does NOT call any external system. Does NOT mutate the original instance.

    Real execution logic (e.g. sending a message, calling an API) must be
    implemented by a concrete subclass or injected handler — not here.
    """

    def execute(self, proposal: ActionProposal) -> ActionProposal:
        """
        Returns a new ActionProposal with status='executed'.
        Raises NotApprovedError if the proposal status is not 'approved'.
        """
        if proposal.status != "approved":
            raise NotApprovedError(
                f"Cannot execute proposal '{proposal.action_id}': "
                f"status is '{proposal.status}', expected 'approved'."
            )
        return replace(proposal, status="executed")
