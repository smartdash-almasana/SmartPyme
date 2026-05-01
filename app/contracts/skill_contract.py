# ruff: noqa: I001

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal


SkillFamily = Literal["development", "project", "business"]
SkillImplementationStatus = Literal["implemented", "partial", "pending", "conceptual"]


@dataclass(frozen=True, slots=True)
class SkillContract:
    """Declarative contract for a SmartPyme skill.

    This contract is not a runtime registry entry. The current executable
    factory model remains app.factory.skills.models.SkillSpec.
    """

    skill_id: str
    family: SkillFamily
    purpose: str
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]
    required_evidence: list[str] = field(default_factory=list)
    allowed_tools: list[str] = field(default_factory=list)
    forbidden_actions: list[str] = field(default_factory=list)
    blocking_conditions: list[str] = field(default_factory=list)
    acceptance_criteria: list[str] = field(default_factory=list)
    implementation_status: SkillImplementationStatus = "conceptual"
    source_files: list[str] = field(default_factory=list)
    next_action: str = ""


@dataclass(frozen=True, slots=True)
class SkillContractCatalog:
    """Versioned list of declarative skill contracts."""

    version: str
    contracts: list[SkillContract]
