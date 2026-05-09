from __future__ import annotations

from factory_v3.ledgers.artifact_ledger import ArtifactLedger
from factory_v3.ledgers.task_ledger import TaskLedger
from factory_v3.runtime.agent_executor import AgentExecutor
from factory_v3.runtime.context_rehydrator import ContextRehydrator


class TaskRuntime:
    def __init__(self):
        self.task_ledger = TaskLedger()
        self.artifact_ledger = ArtifactLedger()
        self.rehydrator = ContextRehydrator(
            task_ledger=self.task_ledger,
            artifact_ledger=self.artifact_ledger,
        )
        self.agent_executor = AgentExecutor(
            task_ledger=self.task_ledger,
            rehydrator=self.rehydrator,
        )
