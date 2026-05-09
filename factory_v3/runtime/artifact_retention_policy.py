from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path


class ArtifactRetentionPolicy:
    def __init__(self, retention_days: int = 30):
        self.retention_days = retention_days

    def expired(self, path: str) -> bool:
        target = Path(path)

        if not target.exists():
            return False

        modified = datetime.utcfromtimestamp(target.stat().st_mtime)
        limit = datetime.utcnow() - timedelta(days=self.retention_days)

        return modified < limit
