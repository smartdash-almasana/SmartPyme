from __future__ import annotations

from datetime import datetime
from typing import Dict


class HeartbeatMonitor:
    def __init__(self):
        self.last_heartbeat: Dict[str, datetime] = {}

    def beat(self, agent_id: str) -> None:
        self.last_heartbeat[agent_id] = datetime.utcnow()

    def get_last_heartbeat(self, agent_id: str) -> datetime | None:
        return self.last_heartbeat.get(agent_id)

    def is_stale(self, agent_id: str, timeout_seconds: int) -> bool:
        last = self.get_last_heartbeat(agent_id)

        if last is None:
            return True

        elapsed = (datetime.utcnow() - last).total_seconds()
        return elapsed > timeout_seconds
