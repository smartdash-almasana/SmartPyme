from __future__ import annotations

from factory_v3.runtime.heartbeat_monitor import HeartbeatMonitor
from factory_v3.runtime.telemetry_bus import TelemetryBus


class RuntimeSupervisor:
    def __init__(
        self,
        *,
        heartbeat_monitor: HeartbeatMonitor,
        telemetry_bus: TelemetryBus,
    ):
        self.heartbeat_monitor = heartbeat_monitor
        self.telemetry_bus = telemetry_bus

    def inspect_agent(self, agent_id: str, timeout_seconds: int = 60) -> bool:
        stale = self.heartbeat_monitor.is_stale(agent_id, timeout_seconds)

        self.telemetry_bus.emit(
            "runtime_supervisor_check",
            {
                "agent_id": agent_id,
                "stale": stale,
            },
        )

        return not stale
