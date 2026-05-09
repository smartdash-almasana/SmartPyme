from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path
from typing import Optional

from factory_v3.contracts.entities import ArtifactEnvelope, ArtifactType


class ArtifactLedger:
    def __init__(self, ledger_path: str = "factory_v3/runtime/ledger.jsonl"):
        self.ledger_path = Path(ledger_path)
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)

        if not self.ledger_path.exists():
            self.ledger_path.touch()

    def register_artifact(self, artifact: ArtifactEnvelope) -> None:
        with self.ledger_path.open("a", encoding="utf-8") as handle:
            handle.write(artifact.model_dump_json())
            handle.write("\n")

    def register_file(
        self,
        *,
        task_id: str,
        artifact_type: ArtifactType,
        storage_path: str,
        producer_id: str,
        metadata: Optional[dict] = None,
    ) -> ArtifactEnvelope:
        content_hash = self._hash_file(storage_path)

        artifact = ArtifactEnvelope(
            task_id=task_id,
            artifact_type=artifact_type,
            storage_path=storage_path,
            content_hash=content_hash,
            producer_id=producer_id,
            metadata=metadata or {},
        )

        self.register_artifact(artifact)

        return artifact

    def get_latest_artifact(
        self,
        task_id: str,
        artifact_type: ArtifactType,
    ) -> Optional[ArtifactEnvelope]:
        latest = None

        with self.ledger_path.open("r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()

                if not line:
                    continue

                payload = json.loads(line)
                artifact = ArtifactEnvelope(**payload)

                if artifact.task_id != task_id:
                    continue

                if artifact.artifact_type != artifact_type:
                    continue

                latest = artifact

        return latest

    @staticmethod
    def _hash_file(path: str) -> str:
        file_path = Path(path)
        content = file_path.read_bytes()
        return sha256(content).hexdigest()
