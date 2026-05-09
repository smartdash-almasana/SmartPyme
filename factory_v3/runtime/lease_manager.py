from datetime import datetime, timedelta


class LeaseManager:
    def __init__(self):
        self._entries = {}

    def acquire(self, key: str, duration_seconds: int = 60) -> bool:
        now = datetime.utcnow()
        current = self._entries.get(key)

        if current and current > now:
            return False

        self._entries[key] = now + timedelta(seconds=duration_seconds)
        return True

    def release(self, key: str) -> None:
        self._entries.pop(key, None)
