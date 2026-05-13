from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from app.contracts.decision_record import DecisionRecord
from app.contracts.execution_guard import enforce_execution_contract
from app.repositories.decision_repository import DecisionRepository


class DecisionOrchestrator:
    """Orchestrator to record owner decisions in a formal and auditable way.

    Boundary rule:
    - Only handles persistence of the decision.
    - Does not execute actions or move job states.
    """

    def record_owner_decision(
        self, input_data: dict[str, Any], cliente_id: str, db_path: str
    ) -> dict[str, Any]:
        # 1. Validation
        if not cliente_id or not isinstance(cliente_id, str):
            return {
                "status": "REJECTED",
                "error_type": "INVALID_INPUT",
                "reason": "cliente_id is required",
            }

        tipo_decision = input_data.get("tipo_decision")
        if tipo_decision not in ("INFORMAR", "EJECUTAR", "RECHAZAR"):
            return {
                "status": "REJECTED",
                "error_type": "INVALID_INPUT",
                "reason": f"Invalid tipo_decision: {tipo_decision}",
            }

        mensaje_original = input_data.get("mensaje_original")
        if not mensaje_original or not isinstance(mensaje_original, str):
            return {
                "status": "REJECTED",
                "error_type": "INVALID_INPUT",
                "reason": "mensaje_original is required",
            }

        propuesta = input_data.get("propuesta")
        if not isinstance(propuesta, dict):
            return {
                "status": "REJECTED",
                "error_type": "INVALID_INPUT",
                "reason": "propuesta must be a dictionary",
            }

        accion = input_data.get("accion")
        if not accion or not isinstance(accion, str):
            return {
                "status": "REJECTED",
                "error_type": "INVALID_INPUT",
                "reason": "accion is required",
            }

        overrides = input_data.get("overrides")
        if overrides is not None and not isinstance(overrides, dict):
            return {
                "status": "REJECTED",
                "error_type": "INVALID_INPUT",
                "reason": "overrides must be a dictionary or None",
            }

        try:
            enforce_execution_contract(
                input_data,
                context="record_owner_decision.input",
                required_fields=(
                    "tipo_decision",
                    "mensaje_original",
                    "propuesta",
                    "accion",
                ),
            )
        except ValueError as ve:
            return {
                "status": "REJECTED",
                "error_type": "INVALID_DECISION_PAYLOAD",
                "reason": str(ve),
            }

        # 2. Preparation
        decision_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()

        record = DecisionRecord(
            decision_id=decision_id,
            cliente_id=cliente_id,
            timestamp=timestamp,
            tipo_decision=tipo_decision,  # type: ignore
            mensaje_original=mensaje_original,
            propuesta=propuesta,
            accion=accion,
            overrides=overrides,
            job_id=input_data.get("job_id"),
        )

        try:
            enforce_execution_contract(record, context="record_owner_decision.record")
        except ValueError as ve:
            return {
                "status": "REJECTED",
                "error_type": "INVALID_DECISION_PAYLOAD",
                "reason": str(ve),
            }

        # 3. Persistence
        try:
            repo = DecisionRepository(cliente_id=cliente_id, db_path=db_path)
            repo.create(record)
        except Exception as e:
            return {
                "status": "REJECTED",
                "error_type": "INTERNAL_ERROR",
                "reason": f"Persistence failed: {str(e)}",
            }

        return {"status": "DECISION_RECORDED", "decision_id": decision_id}


def record_owner_decision(
    input_data: dict[str, Any], cliente_id: str, db_path: str
) -> dict[str, Any]:
    """Standalone function to record owner decision."""
    return DecisionOrchestrator().record_owner_decision(input_data, cliente_id, db_path)
