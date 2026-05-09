from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


class PromptContract(BaseModel):
    context: str
    role: str
    instruction: str
    examples: List[str] = Field(default_factory=list)
    borders: List[str] = Field(default_factory=list)

    def render(self) -> str:
        sections = [
            f"CONTEXT:\n{self.context}",
            f"ROLE:\n{self.role}",
            f"INSTRUCTION:\n{self.instruction}",
        ]

        if self.examples:
            sections.append("EXAMPLES:\n" + "\n".join(self.examples))

        if self.borders:
            sections.append("BORDERS:\n" + "\n".join(self.borders))

        return "\n\n".join(sections)
