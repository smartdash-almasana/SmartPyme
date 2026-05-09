from __future__ import annotations

from collections import defaultdict


class RetryManager:
    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries
        self.retry_counts = defaultdict(int)

    def should_retry(self, task_id: str) -> bool:
        return self.retry_counts[task_id] < self.max_retries

    def register_retry(self, task_id: str) -> int:
        self.retry_counts[task_id] += 1
        return self.retry_counts[task_id]

    def reset(self, task_id: str) -> None:
        self.retry_counts.pop(task_id, None)
