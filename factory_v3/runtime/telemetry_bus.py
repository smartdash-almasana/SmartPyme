from __future__ import annotations

from datetime import datetime
from pathlib import Path


class TelemetryBus:
    def __init__(self, bus_path: str = "factory_v3/runtime/telemetry.jsonl"):
        self.bus_path = Path(bus_path)
        self.bus_path.parent.mkdir(parents=True, exist_ok=True)

        if not self.bus_path.exists():
            self.bus_path.touch()

    def emit(self, event_type: str, payload: dict) -> None:
        record = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "payload": payload,
        }

        with self.bus_path.open("a", encoding="utf-8") as handle:
            handle.write(str(record))
            handle.write("\n")
