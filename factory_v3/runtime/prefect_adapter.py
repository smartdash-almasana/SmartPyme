from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PrefectTaskSignal:
    task_id: str


class PrefectAdapter:
    def dispatch(self, signal: PrefectTaskSignal) -> None:
        raise NotImplementedError("Prefect adapter not connected")
