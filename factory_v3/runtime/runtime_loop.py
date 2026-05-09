from __future__ import annotations

from factory_v3.runtime.metrics_registry import MetricsRegistry
from factory_v3.runtime.recovery_manager import RecoveryManager
from factory_v3.runtime.task_scheduler import TaskScheduler
from factory_v3.runtime.telemetry_bus import TelemetryBus


class RuntimeLoop:
    def __init__(
        self,
        *,
        scheduler: TaskScheduler,
        recovery_manager: RecoveryManager,
        telemetry_bus: TelemetryBus,
        metrics_registry: MetricsRegistry,
    ):
        self.scheduler = scheduler
        self.recovery_manager = recovery_manager
        self.telemetry_bus = telemetry_bus
        self.metrics_registry = metrics_registry

    def tick(self) -> dict:
        pending_tasks = self.scheduler.get_pending_tasks()
        failed_tasks = self.scheduler.get_failed_tasks()
        recovered_tasks = self.recovery_manager.recover_failed_tasks()

        self.metrics_registry.increment("runtime_ticks")
        self.metrics_registry.increment("pending_tasks", len(pending_tasks))
        self.metrics_registry.increment("failed_tasks", len(failed_tasks))

        self.telemetry_bus.emit(
            "runtime_tick",
            {
                "pending_tasks": pending_tasks,
                "failed_tasks": failed_tasks,
                "recovered_tasks": recovered_tasks,
            },
        )

        return {
            "pending_tasks": pending_tasks,
            "failed_tasks": failed_tasks,
            "recovered_tasks": recovered_tasks,
            "metrics": self.metrics_registry.snapshot(),
        }
