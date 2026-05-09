from __future__ import annotations

from factory_v3.contracts.entities import TaskState
from factory_v3.runtime.event_replayer import EventReplayer
from factory_v3.runtime.task_scheduler import TaskScheduler


class RecoveryManager:
    def __init__(
        self,
        *,
        scheduler: TaskScheduler,
        event_replayer: EventReplayer,
    ):
        self.scheduler = scheduler
        self.event_replayer = event_replayer

    def recover_failed_tasks(self) -> list[str]:
        recovered = []

        for task_id in self.scheduler.get_failed_tasks():
            snapshot = self.event_replayer.replay(task_id)

            if snapshot.state == TaskState.FAILED:
                recovered.append(task_id)

        return recovered
