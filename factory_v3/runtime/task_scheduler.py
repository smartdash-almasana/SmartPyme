from __future__ import annotations

from typing import List

from factory_v3.contracts.entities import TaskState
from factory_v3.ledgers.task_ledger import TaskLedger


class TaskScheduler:
    def __init__(self, task_ledger: TaskLedger):
        self.task_ledger = task_ledger

    def get_pending_tasks(self) -> List[str]:
        return self.task_ledger.get_tasks_by_state(TaskState.PENDING)

    def get_failed_tasks(self) -> List[str]:
        return self.task_ledger.get_tasks_by_state(TaskState.FAILED)

    def next_task(self) -> str | None:
        pending = self.get_pending_tasks()

        if not pending:
            return None

        return pending[0]
