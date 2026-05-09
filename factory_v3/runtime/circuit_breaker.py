from __future__ import annotations

from enum import Enum


class CircuitState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"


class CircuitBreaker:
    def __init__(self, failure_threshold: int = 3):
        self.failure_threshold = failure_threshold
        self.failure_count = 0
        self.state = CircuitState.CLOSED

    def register_failure(self) -> None:
        self.failure_count += 1

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN

    def reset(self) -> None:
        self.failure_count = 0
        self.state = CircuitState.CLOSED

    def can_execute(self) -> bool:
        return self.state == CircuitState.CLOSED
