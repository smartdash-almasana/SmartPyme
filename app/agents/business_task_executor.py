from __future__ import annotations

import os
from pathlib import Path
from typing import Any
from uuid import uuid4

from app.contracts.formula_contract import FormulaInput, FormulaResult
from app.contracts.pathology_contract import PathologyFinding
from app.agents.formula_calculation_agent import FormulaCalculationAgent
from app.agents.pathology_auditor_agent import PathologyAuditorAgent

AUDIT_VENTA_BAJO_COSTO = "audit_venta_bajo_costo"


class BusinessTaskExecutor:
    def __init__(
        self,
        formula_results_db_path: str | Path | None = None,
        pathologies_db_path: str | Path | None = None,
    ) -> None:
        self.formula_results_db_path = Path(
            formula_results_db_path
            or os.getenv("SMARTPYME_FORMULA_RESULTS_DB_PATH", "data/formula_results.db")
        )
        self.pathologies_db_path = Path(
            pathologies_db_path
            or os.getenv("SMARTPYME_PATHOLOGIES_DB_PATH", "data/pathologies.db")
        )

    def execute(self, task_type: str, payload: dict[str, Any]) -> dict[str, Any]:
        if task_type != AUDIT_VENTA_BAJO_COSTO:
            raise ValueError(f"Unsupported business task: {task_type}")

        return self.audit_venta_bajo_costo(payload)

    def audit_venta_bajo_costo(self, payload: dict[str, Any]) -> dict[str, Any]:
        cliente_id = _require_non_empty_string(payload, "cliente_id")
        ventas = _require_number(payload, "ventas")
        costos = _require_number(payload, "costos")
        source_refs = _coerce_source_refs(payload.get("source_refs", []))

        formula_result_id = str(payload.get("formula_result_id") or uuid4())
        pathology_finding_id = str(
            payload.get("pathology_finding_id")
            or f"venta_bajo_costo:{formula_result_id}"
        )

        formula_result = FormulaCalculationAgent(
            cliente_id=cliente_id,
            db_path=self.formula_results_db_path,
        ).calculate_and_persist(
            "ganancia_bruta",
            [
                FormulaInput(name="ventas", value=ventas, source_refs=source_refs),
                FormulaInput(name="costos", value=costos, source_refs=source_refs),
            ],
            result_id=formula_result_id,
        )

        pathology_finding = PathologyAuditorAgent(
            cliente_id=cliente_id,
            formula_results_db_path=self.formula_results_db_path,
            pathologies_db_path=self.pathologies_db_path,
        ).audit_formula_result(
            formula_result_id=formula_result_id,
            pathology_id="venta_bajo_costo",
            pathology_finding_id=pathology_finding_id,
        )

        if pathology_finding is None:
            raise RuntimeError("FormulaResult persisted but not readable for pathology audit")

        return _serialize_execution_result(
            cliente_id=cliente_id,
            task_type=AUDIT_VENTA_BAJO_COSTO,
            formula_result_id=formula_result_id,
            formula_result=formula_result,
            pathology_finding_id=pathology_finding_id,
            pathology_finding=pathology_finding,
        )


def _require_non_empty_string(payload: dict[str, Any], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} is required")
    return value.strip()


def _require_number(payload: dict[str, Any], key: str) -> float | int:
    value = payload.get(key)
    if not isinstance(value, (float, int)) or isinstance(value, bool):
        raise ValueError(f"{key} must be numeric")
    return value


def _coerce_source_refs(value: Any) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError("source_refs must be a list")
    if not all(isinstance(item, str) for item in value):
        raise ValueError("source_refs must contain only strings")
    return value


def _serialize_execution_result(
    *,
    cliente_id: str,
    task_type: str,
    formula_result_id: str,
    formula_result: FormulaResult,
    pathology_finding_id: str,
    pathology_finding: PathologyFinding,
) -> dict[str, Any]:
    return {
        "cliente_id": cliente_id,
        "task_type": task_type,
        "formula_result_id": formula_result_id,
        "formula_result": formula_result.model_dump(mode="json"),
        "pathology_finding_id": pathology_finding_id,
        "pathology_finding": pathology_finding.model_dump(mode="json"),
    }
