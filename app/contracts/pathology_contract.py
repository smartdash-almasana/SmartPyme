from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from app.contracts.formula_contract import FormulaResult, FormulaStatus


class PathologyStatus(str, Enum):
    ACTIVE = "ACTIVE"
    NOT_DETECTED = "NOT_DETECTED"
    PENDING_DATA = "PENDING_DATA"


class PathologySeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class PathologyDefinition(BaseModel):
    pathology_id: str
    formula_id: str
    description: str
    severity: PathologySeverity
    suggested_action: str


class PathologyEvaluationInput(BaseModel):
    cliente_id: str
    formula_result_id: str
    formula_result: FormulaResult


class PathologyFinding(BaseModel):
    cliente_id: str
    pathology_id: str
    formula_result_id: str
    formula_id: str
    status: PathologyStatus
    severity: PathologySeverity | None = None
    suggested_action: str | None = None
    source_refs: list[str] = Field(default_factory=list)
    explanation: str
    metadata: dict[str, Any] = Field(default_factory=dict)


SUPPORTED_PATHOLOGIES: dict[str, PathologyDefinition] = {
    "margen_bruto_negativo": PathologyDefinition(
        pathology_id="margen_bruto_negativo",
        formula_id="margen_bruto",
        description="Detecta margen bruto negativo.",
        severity=PathologySeverity.HIGH,
        suggested_action="Revisar costos de materia prima o ajustar precios de venta.",
    ),
}


def evaluate_pathology(pathology_id: str, payload: PathologyEvaluationInput) -> PathologyFinding:
    if pathology_id not in SUPPORTED_PATHOLOGIES:
        return PathologyFinding(
            cliente_id=payload.cliente_id,
            pathology_id=pathology_id,
            formula_result_id=payload.formula_result_id,
            formula_id=payload.formula_result.formula_id,
            status=PathologyStatus.PENDING_DATA,
            source_refs=payload.formula_result.source_refs,
            explanation="Patología no soportada por el catálogo.",
            metadata={"blocking_reason": "PATHOLOGY_NOT_SUPPORTED"},
        )

    definition = SUPPORTED_PATHOLOGIES[pathology_id]
    result = payload.formula_result

    if result.status == FormulaStatus.BLOCKED:
        return PathologyFinding(
            cliente_id=payload.cliente_id,
            pathology_id=pathology_id,
            formula_result_id=payload.formula_result_id,
            formula_id=result.formula_id,
            status=PathologyStatus.PENDING_DATA,
            source_refs=result.source_refs,
            explanation="No se puede evaluar la patología porque la fórmula está bloqueada.",
            metadata={"blocking_reason": result.blocking_reason},
        )

    if result.formula_id != definition.formula_id:
        return PathologyFinding(
            cliente_id=payload.cliente_id,
            pathology_id=pathology_id,
            formula_result_id=payload.formula_result_id,
            formula_id=result.formula_id,
            status=PathologyStatus.PENDING_DATA,
            source_refs=result.source_refs,
            explanation="La fórmula calculada no coincide con la patología solicitada.",
            metadata={"expected_formula_id": definition.formula_id},
        )

    if pathology_id == "margen_bruto_negativo" and result.value is not None and result.value < 0:
        return PathologyFinding(
            cliente_id=payload.cliente_id,
            pathology_id=pathology_id,
            formula_result_id=payload.formula_result_id,
            formula_id=result.formula_id,
            status=PathologyStatus.ACTIVE,
            severity=definition.severity,
            suggested_action=definition.suggested_action,
            source_refs=result.source_refs,
            explanation=f"El margen bruto calculado es {result.value}, lo cual indica pérdida.",
        )

    return PathologyFinding(
        cliente_id=payload.cliente_id,
        pathology_id=pathology_id,
        formula_result_id=payload.formula_result_id,
        formula_id=result.formula_id,
        status=PathologyStatus.NOT_DETECTED,
        source_refs=result.source_refs,
        explanation="No se detectó la patología con el resultado calculado.",
    )
