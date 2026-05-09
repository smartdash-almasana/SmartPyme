from __future__ import annotations

from pydantic import BaseModel, Field


class DivergentProfile(BaseModel):
    name: str
    perspective: str
    core_questions: list[str] = Field(default_factory=list)


class DivergentPanelResult(BaseModel):
    tensions: list[str] = Field(default_factory=list)
    invariants: list[str] = Field(default_factory=list)


class DivergentPanel:
    def run(self, profiles: list[DivergentProfile]) -> DivergentPanelResult:
        tensions = []
        invariants = []

        for profile in profiles:
            if profile.core_questions:
                tensions.append(profile.core_questions[0])

        invariants.extend([
            "auditability",
            "rollback capability",
            "human override",
        ])

        return DivergentPanelResult(
            tensions=tensions[:3],
            invariants=invariants[:3],
        )
