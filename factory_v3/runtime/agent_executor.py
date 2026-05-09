from __future__ import annotations

from typing import Callable

from factory_v3.contracts.entities import TaskState
from factory_v3.ledgers.task_ledger import TaskLedger
from factory_v3.runtime.context_rehydrator import ContextRehydrator


class AgentExecutor:
    def __init__(
        self,
        *,
        task_ledger: TaskLedger,
        rehydrator: ContextRehydrator,
    ):
        self.task_ledger = task_ledger
        self.rehydrator = rehydrator

    def execute(
        self,
        *,
        task_id: str,
        agent_id: str,
        execution_callable: Callable,
    ):
        current_state = self.task_ledger.get_latest_state(task_id)

        self.task_ledger.transition_task(
            task_id=task_id,
            previous_state=current_state,
            next_state=TaskState.ACTIVE,
            producer_id=agent_id,
            reason="agent execution started",
        )

        snapshot = self.rehydrator.rebuild_task_context(task_id)

        try:
            result = execution_callable(snapshot)

            self.task_ledger.transition_task(
                task_id=task_id,
                previous_state=TaskState.ACTIVE,
                next_state=TaskState.DONE,
                producer_id=agent_id,
                reason="agent execution completed",
            )

            return result

        except Exception as exc:
            self.task_ledger.transition_task(
                task_id=task_id,
                previous_state=TaskState.ACTIVE,
                next_state=TaskState.FAILED,
                producer_id=agent_id,
                reason=str(exc),
            )

            raise
