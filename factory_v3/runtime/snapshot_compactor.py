from __future__ import annotations

from factory_v3.runtime.context_rehydrator import ContextRehydrator
from factory_v3.runtime.runtime_snapshot import RuntimeSnapshot


class SnapshotCompactor:
    def __init__(self, rehydrator: ContextRehydrator):
        self.rehydrator = rehydrator

    def compact(self, task_id: str) -> RuntimeSnapshot:
        return self.rehydrator.rebuild_task_context(task_id)
