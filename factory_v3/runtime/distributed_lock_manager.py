from __future__ import annotations

from pathlib import Path


class DistributedLockManager:
    def __init__(self, lock_root: str = "factory_v3/runtime/locks"):
        self.lock_root = Path(lock_root)
        self.lock_root.mkdir(parents=True, exist_ok=True)

    def acquire(self, lock_id: str) -> bool:
        lock_file = self.lock_root / f"{lock_id}.lock"

        if lock_file.exists():
            return False

        lock_file.write_text("locked", encoding="utf-8")
        return True

    def release(self, lock_id: str) -> None:
        lock_file = self.lock_root / f"{lock_id}.lock"

        if lock_file.exists():
            lock_file.unlink()
