from __future__ import annotations

from collections import defaultdict
from typing import Dict, List

from factory_v3.contracts.entities import ArtifactEnvelope


class ArtifactGraphIndex:
    def __init__(self):
        self.parent_to_children: Dict[str, List[str]] = defaultdict(list)
        self.artifacts: Dict[str, ArtifactEnvelope] = {}

    def register(self, artifact: ArtifactEnvelope) -> None:
        self.artifacts[artifact.artifact_id] = artifact

        for parent_id in artifact.parent_artifacts:
            self.parent_to_children[parent_id].append(artifact.artifact_id)

    def get_children(self, artifact_id: str) -> List[str]:
        return self.parent_to_children.get(artifact_id, [])

    def get_artifact(self, artifact_id: str) -> ArtifactEnvelope | None:
        return self.artifacts.get(artifact_id)
