from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class FormulaStatus(StrEnum):
    OK = "OK"
    BLOCKED = "BLOCKED"


class FormulaInput(BaseModel):
    name: str
    value: float | int | None
    source_refs: list[str] = Field(default_factory=list)


class FormulaDefinition(BaseModel):
    formula_id: str
    required_inputs: list[str]
    description: str


class FormulaResult(BaseModel):
    formula_id: str
    status: FormulaStatus
    value: float | None
    inputs: dict[str, float | int | None]
    source_refs: list[str] = Field(default_factory=list)
    blocking_reason: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


SUPPORTED_FORMULAS: dict[str, FormulaDefinition] = {
    "margen_bruto": FormulaDefinition(
        formula_id="margen_bruto",
        required_inputs=["ventas", "costos"],
        description="(ventas - costos) / ventas",
    ),
    "ganancia_bruta": FormulaDefinition(
        formula_id="ganancia_bruta",
        required_inputs=["ventas", "costos"],
        description="ventas - costos",
    ),
}


def calculate_formula(formula_id: str, inputs: list[FormulaInput]) -> FormulaResult:
    from app.services.formula_engine_service import FormulaEngineService

    return FormulaEngineService().calculate(formula_id, inputs)
