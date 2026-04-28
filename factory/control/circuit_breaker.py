"""Circuit breaker primitives for SmartPyme Factory v2.1."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone


@dataclass
class CircuitBreaker:
    max_failures_per_hour: int = 10
    cooldown_minutes: int = 60
    failures: list[datetime] = field(default_factory=list)
    tripped_until: datetime | None = None

    def _now(self, at: datetime | None = None) -> datetime:
        now = at or datetime.now(timezone.utc)
        return now if now.tzinfo else now.replace(tzinfo=timezone.utc)

    def record_failure(self, at: datetime | None = None) -> bool:
        now = self._now(at)
        window_start = now - timedelta(hours=1)
        self.failures = [item for item in self.failures if self._now(item) >= window_start]
        self.failures.append(now)
        if len(self.failures) > self.max_failures_per_hour:
            self.tripped_until = now + timedelta(minutes=self.cooldown_minutes)
            return True
        return False

    def is_open(self, at: datetime | None = None) -> bool:
        now = self._now(at)
        return self.tripped_until is not None and now < self.tripped_until

    def reset(self) -> None:
        self.failures.clear()
        self.tripped_until = None

    def snapshot(self) -> dict[str, object]:
        return {
            "failures_last_hour": len(self.failures),
            "is_open": self.is_open(),
            "tripped_until": self.tripped_until.isoformat() if self.tripped_until else None,
        }
