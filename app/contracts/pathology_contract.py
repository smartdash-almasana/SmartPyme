from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from app.contracts.formula_contract import FormulaResult


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
    from app.services.pathology_engine_service import PathologyEngineService

    return PathologyEngineService().evaluate(pathology_id, payload)
