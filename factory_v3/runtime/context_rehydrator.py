from __future__ import annotations

import json
from pathlib import Path

from factory_v3.ledgers.artifact_ledger import ArtifactLedger
from factory_v3.ledgers.task_ledger import TaskLedger
from factory_v3.runtime.runtime_snapshot import RuntimeSnapshot


class ContextRehydrator:
    def __init__(
        self,
        task_ledger: TaskLedger,
        artifact_ledger: ArtifactLedger,
    ):
        self.task_ledger = task_ledger
        self.artifact_ledger = artifact_ledger

    def rebuild_task_context(self, task_id: str) -> RuntimeSnapshot:
        events = self.task_ledger.get_events(task_id)

        artifact_ids = []

        ledger_path = self.artifact_ledger.ledger_path

        if ledger_path.exists():
            with ledger_path.open("r", encoding="utf-8") as handle:
                for line in handle:
                    line = line.strip()

                    if not line:
                        continue

                    payload = json.loads(line)

                    if payload.get("task_id") != task_id:
                        continue

                    artifact_ids.append(payload.get("artifact_id"))

        latest_state = self.task_ledger.get_latest_state(task_id)

        return RuntimeSnapshot(
            task_id=task_id,
            state=latest_state,
            event_count=len(events),
            artifact_ids=artifact_ids,
        )
