from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ADKExecutionRequest:
    task_id: str
    agent_id: str
    objective: str


class ADKAdapter:
    def execute(self, request: ADKExecutionRequest):
        raise NotImplementedError("ADK runtime adapter not connected")
