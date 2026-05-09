from __future__ import annotations

from pathlib import Path

from factory_v3.runtime.runtime_snapshot import RuntimeSnapshot


class SnapshotStore:
    def __init__(self, root_path: str = "factory_v3/runtime/snapshots"):
        self.root_path = Path(root_path)
        self.root_path.mkdir(parents=True, exist_ok=True)

    def save(self, snapshot: RuntimeSnapshot) -> Path:
        target = self.root_path / f"{snapshot.task_id}.json"
        target.write_text(snapshot.model_dump_json(), encoding="utf-8")
        return target

    def load(self, task_id: str) -> RuntimeSnapshot | None:
        target = self.root_path / f"{task_id}.json"

        if not target.exists():
            return None

        return RuntimeSnapshot.model_validate_json(target.read_text(encoding="utf-8"))
