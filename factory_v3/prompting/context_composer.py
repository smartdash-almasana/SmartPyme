from __future__ import annotations

from typing import Iterable


class ContextComposer:
    def compose(self, artifacts: Iterable[str], constraints: Iterable[str]) -> str:
        sections = []

        for artifact in artifacts:
            sections.append(f"ARTIFACT:\n{artifact}")

        for constraint in constraints:
            sections.append(f"CONSTRAINT:\n{constraint}")

        return "\n\n".join(sections)
