from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

from app.contracts.action_contract import ActionProposal

if TYPE_CHECKING:
    from app.contracts.execution_adapter_contract import ExecutionAdapter


class NotApprovedError(Exception):
    """Raised when execute() is called on a proposal that is not approved."""


class AdapterExecutionError(Exception):
    """Raised when the adapter returns status != 'executed'."""


class ActionExecutionService:
    """
    Marks an approved ActionProposal as executed.
    Returns a NEW ActionProposal with status='executed'.
    Does NOT mutate the original instance.

    Without adapter: marks executed internally (no external call).
    With adapter:    delegates to adapter.execute(proposal).
                     Only marks executed if adapter_result.status == 'executed'.
                     If adapter returns 'blocked' or 'failed', raises AdapterExecutionError.
    """

    def __init__(self, adapter: "ExecutionAdapter | None" = None) -> None:
        self.adapter = adapter

    def execute(self, proposal: ActionProposal) -> ActionProposal:
        """
        Returns a new ActionProposal with status='executed'.
        Raises NotApprovedError if proposal.status != 'approved'.
        Raises AdapterExecutionError if adapter returns blocked/failed.
        """
        if proposal.status != "approved":
            raise NotApprovedError(
                f"Cannot execute proposal '{proposal.action_id}': "
                f"status is '{proposal.status}', expected 'approved'."
            )

        if self.adapter is not None:
            result = self.adapter.execute(proposal)
            if result.status != "executed":
                raise AdapterExecutionError(
                    f"Adapter '{result.adapter_id}' returned status='{result.status}' "
                    f"for proposal '{proposal.action_id}': {result.message}"
                )

        return replace(proposal, status="executed")
