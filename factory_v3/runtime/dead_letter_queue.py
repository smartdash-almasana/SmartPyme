from __future__ import annotations

from pathlib import Path


class DeadLetterQueue:
    def __init__(self, queue_path: str = "factory_v3/runtime/dead_letter_queue.jsonl"):
        self.queue_path = Path(queue_path)
        self.queue_path.parent.mkdir(parents=True, exist_ok=True)

        if not self.queue_path.exists():
            self.queue_path.touch()

    def push(self, payload: str) -> None:
        with self.queue_path.open("a", encoding="utf-8") as handle:
            handle.write(payload)
            handle.write("\n")
