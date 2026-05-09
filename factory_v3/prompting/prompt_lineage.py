from __future__ import annotations

from collections import defaultdict
from typing import Dict, List

from factory_v3.prompting.prompt_versioning import PromptVersion


class PromptLineage:
    def __init__(self):
        self.lineage: Dict[str, List[str]] = defaultdict(list)
        self.versions: Dict[str, PromptVersion] = {}

    def register(
        self,
        version: PromptVersion,
        parent_version_id: str | None = None,
    ) -> None:
        self.versions[version.version_id] = version

        if parent_version_id:
            self.lineage[parent_version_id].append(version.version_id)

    def get_children(self, version_id: str) -> List[str]:
        return self.lineage.get(version_id, [])

    def get_version(self, version_id: str) -> PromptVersion | None:
        return self.versions.get(version_id)
