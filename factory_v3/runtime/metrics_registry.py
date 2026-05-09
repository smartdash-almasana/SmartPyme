from __future__ import annotations

from collections import defaultdict
from typing import Dict


class MetricsRegistry:
    def __init__(self):
        self.counters: Dict[str, int] = defaultdict(int)

    def increment(self, metric_name: str, amount: int = 1) -> int:
        self.counters[metric_name] += amount
        return self.counters[metric_name]

    def get(self, metric_name: str) -> int:
        return self.counters.get(metric_name, 0)

    def snapshot(self) -> dict[str, int]:
        return dict(self.counters)
