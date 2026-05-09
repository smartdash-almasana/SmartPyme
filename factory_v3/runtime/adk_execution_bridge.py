from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ADKExecutionEnvelope:
    task_id: str
    agent_id: str
    objective: str


class ADKExecutionBridge:
    def execute(self, envelope: ADKExecutionEnvelope):
        raise NotImplementedError("ADK execution bridge not connected")
