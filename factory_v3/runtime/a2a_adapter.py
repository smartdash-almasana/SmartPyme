from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class A2ATaskMessage:
    task_id: str
    sender_agent: str
    receiver_agent: str
    payload: dict[str, Any]


class A2ATransportAdapter:
    def send(self, message: A2ATaskMessage) -> None:
        raise NotImplementedError("A2A transport adapter not connected")
