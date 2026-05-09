from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class PersistentQueue:
    def __init__(self, queue_path: str = "factory_v3/runtime/persistent_queue.jsonl"):
        self.queue_path = Path(queue_path)
        self.queue_path.parent.mkdir(parents=True, exist_ok=True)

        if not self.queue_path.exists():
            self.queue_path.touch()

    def enqueue(self, payload: dict[str, Any]) -> None:
        with self.queue_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload))
            handle.write("\n")

    def read_all(self) -> list[dict[str, Any]]:
        results = []

        with self.queue_path.open("r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()

                if not line:
                    continue

                results.append(json.loads(line))

        return results
