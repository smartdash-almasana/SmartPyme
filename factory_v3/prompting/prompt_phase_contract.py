from __future__ import annotations

from enum import Enum

from pydantic import BaseModel


class PromptPhase(str, Enum):
    QUALITY_GATE = "quality_gate"
    IDENTITY = "identity"
    EXPERT_PANEL = "expert_panel"
    ARCHITECTURE = "architecture"
    REFINEMENT = "refinement"


class PromptPhaseContract(BaseModel):
    phase: PromptPhase
    objective: str
    required_inputs: list[str] = []
    expected_outputs: list[str] = []
