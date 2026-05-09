from __future__ import annotations

from pydantic import BaseModel, Field

from factory_v3.prompting.prompt_contract import PromptContract


class PromptQualityScore(BaseModel):
    clarity: int = 0
    precision: int = 0
    completeness: int = 0
    relevance: int = 0
    threshold: int = 32
    missing_data: list[str] = Field(default_factory=list)

    @property
    def total(self) -> int:
        return self.clarity + self.precision + self.completeness + self.relevance

    @property
    def passed(self) -> bool:
        return self.total >= self.threshold


class PromptQualityGate:
    def evaluate(self, contract: PromptContract) -> PromptQualityScore:
        missing_data: list[str] = []

        clarity = 10 if contract.instruction.strip() else 0
        precision = 10 if contract.role.strip() else 0
        completeness = 10 if contract.context.strip() else 0
        relevance = 10 if contract.borders else 6

        if not contract.instruction.strip():
            missing_data.append("instruction")

        if not contract.role.strip():
            missing_data.append("role")

        if not contract.context.strip():
            missing_data.append("context")

        if not contract.borders:
            missing_data.append("borders")

        return PromptQualityScore(
            clarity=clarity,
            precision=precision,
            completeness=completeness,
            relevance=relevance,
            missing_data=missing_data,
        )
