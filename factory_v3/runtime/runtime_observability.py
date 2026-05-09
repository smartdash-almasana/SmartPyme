from __future__ import annotations

from pydantic import BaseModel

from factory_v3.runtime.agent_registry import AgentRegistry
from factory_v3.runtime.metrics_registry import MetricsRegistry
from factory_v3.runtime.persistent_queue import PersistentQueue
from factory_v3.runtime.task_scheduler import TaskScheduler


class RuntimeObservabilitySnapshot(BaseModel):
    pending_tasks: int = 0
    failed_tasks: int = 0
    registered_agents: int = 0
    queue_depth: int = 0
    metrics: dict = {}


class RuntimeObservability:
    def __init__(
        self,
        *,
        scheduler: TaskScheduler,
        registry: AgentRegistry,
        queue: PersistentQueue,
        metrics: MetricsRegistry,
    ):
        self.scheduler = scheduler
        self.registry = registry
        self.queue = queue
        self.metrics = metrics

    def snapshot(self) -> RuntimeObservabilitySnapshot:
        return RuntimeObservabilitySnapshot(
            pending_tasks=len(self.scheduler.get_pending_tasks()),
            failed_tasks=len(self.scheduler.get_failed_tasks()),
            registered_agents=len(self.registry.list_agents()),
            queue_depth=len(self.queue.read_all()),
            metrics=self.metrics.snapshot(),
        )
