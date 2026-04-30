from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class FormulaStatus(str, Enum):
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
    if formula_id not in SUPPORTED_FORMULAS:
        return FormulaResult(
            formula_id=formula_id,
            status=FormulaStatus.BLOCKED,
            value=None,
            inputs={input_item.name: input_item.value for input_item in inputs},
            source_refs=_collect_source_refs(inputs),
            blocking_reason="FORMULA_NOT_SUPPORTED",
        )

    values = {input_item.name: input_item.value for input_item in inputs}
    source_refs = _collect_source_refs(inputs)
    definition = SUPPORTED_FORMULAS[formula_id]

    missing = [name for name in definition.required_inputs if values.get(name) is None]
    if missing:
        return FormulaResult(
            formula_id=formula_id,
            status=FormulaStatus.BLOCKED,
            value=None,
            inputs=values,
            source_refs=source_refs,
            blocking_reason=f"MISSING_INPUTS: {','.join(missing)}",
        )

    ventas = values["ventas"]
    costos = values["costos"]

    if formula_id == "margen_bruto":
        if ventas == 0:
            return FormulaResult(
                formula_id=formula_id,
                status=FormulaStatus.BLOCKED,
                value=None,
                inputs=values,
                source_refs=source_refs,
                blocking_reason="DIVISION_BY_ZERO: ventas",
            )
        value = (ventas - costos) / ventas
    elif formula_id == "ganancia_bruta":
        value = ventas - costos
    else:
        return FormulaResult(
            formula_id=formula_id,
            status=FormulaStatus.BLOCKED,
            value=None,
            inputs=values,
            source_refs=source_refs,
            blocking_reason="FORMULA_NOT_IMPLEMENTED",
        )

    return FormulaResult(
        formula_id=formula_id,
        status=FormulaStatus.OK,
        value=float(value),
        inputs=values,
        source_refs=source_refs,
    )


def _collect_source_refs(inputs: list[FormulaInput]) -> list[str]:
    refs: list[str] = []
    for input_item in inputs:
        refs.extend(input_item.source_refs)
    return refs
