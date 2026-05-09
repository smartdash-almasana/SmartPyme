from __future__ import annotations

from factory_v3.ledgers.task_ledger import TaskLedger
from factory_v3.runtime.context_rehydrator import ContextRehydrator
from factory_v3.runtime.runtime_snapshot import RuntimeSnapshot


class EventReplayer:
    def __init__(
        self,
        *,
        task_ledger: TaskLedger,
        rehydrator: ContextRehydrator,
    ):
        self.task_ledger = task_ledger
        self.rehydrator = rehydrator

    def replay(self, task_id: str) -> RuntimeSnapshot:
        return self.rehydrator.rebuild_task_context(task_id)
