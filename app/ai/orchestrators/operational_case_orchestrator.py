from __future__ import annotations

import uuid
from typing import Any
from app.contracts.operational_case_contract import OperationalCase
from app.orchestrator.models import STATE_RUNNING


class OperationalCaseOrchestrator:
    """Orchestrator to transform a RUNNING job into an investigative OperationalCase."""

    def build_operational_case(
        self,
        cliente_id: str,
        job_id: str,
        job_repository: Any,
        operational_case_repository: Any,
    ) -> dict[str, Any]:
        try:
            # 1. Fetch Job
            job_data = job_repository.get_job(job_id)
            if not job_data:
                return {
                    "status": "REJECTED",
                    "error_type": "JOB_NOT_FOUND",
                    "reason": f"Job {job_id} not found",
                }

            # 2. Isolation and State Validation
            payload = job_data.get("payload", {})
            job_cliente_id = payload.get("cliente_id")
            
            # If not in top payload, check operational_plan
            if not job_cliente_id:
                job_cliente_id = payload.get("operational_plan", {}).get("cliente_id")

            if job_cliente_id != cliente_id:
                return {
                    "status": "REJECTED",
                    "error_type": "JOB_NOT_FOUND",
                    "reason": "Isolation violation or job not found for this client",
                }

            current_state = job_data.get("current_state")
            if current_state != STATE_RUNNING:
                return {
                    "status": "REJECTED",
                    "error_type": "JOB_NOT_RUNNING",
                    "reason": f"Job state is {current_state}, must be {STATE_RUNNING}",
                }

            # 3. Extract and Validate metadata (Hardening)
            skill_id = job_data.get("skill_id")
            objective = payload.get("objective") or payload.get("operational_plan", {}).get("objective")
            demanda_original = (
                payload.get("owner_request") 
                or payload.get("operational_plan", {}).get("owner_request") 
                or (objective if objective else None)
            )
            
            variables = payload.get("variables") or payload.get("operational_plan", {}).get("variables") or {}
            evidence = payload.get("evidence") or payload.get("operational_plan", {}).get("required_sources") or []

            # Principio de interacción: Aclaraciones precisas
            if not demanda_original:
                return {
                    "status": "CLARIFICATION_REQUIRED",
                    "reason": "INSUFFICIENT_CONTEXT",
                    "missing": ["demanda_original"],
                    "owner_message": "Necesito que me cuentes qué querés investigar o resolver para poder armar el caso."
                }
                
            if not skill_id:
                return {
                    "status": "CLARIFICATION_REQUIRED",
                    "reason": "INSUFFICIENT_CONTEXT",
                    "missing": ["skill_id"],
                    "owner_message": "Necesito identificar qué tipo de trabajo querés hacer antes de avanzar."
                }
                
            if not variables and not evidence:
                return {
                    "status": "CLARIFICATION_REQUIRED",
                    "reason": "INSUFFICIENT_CONTEXT",
                    "missing": ["variables_curadas", "evidencia_disponible"],
                    "owner_message": "Para avanzar necesito al menos datos concretos o evidencia: por ejemplo un Excel, facturas, extractos, fotos útiles o valores cargados manualmente."
                }

            # 4. Formulate Hypothesis
            # Ensure semantic rule: "Investigar si..."
            hypothesis_base = objective or demanda_original
            hypothesis = f"Investigar si {hypothesis_base}"
            if not hypothesis.endswith("?"):
                hypothesis += "?"

            # 5. Build OperationalCase
            case_id = str(uuid.uuid4())
            
            # Default investigation plan based on skill_id
            plan = ["Load Evidence", "Apply Formula", "Generate Findings"]
            if skill_id and "reconciliation" in skill_id:
                plan = ["Fetch Sources", "Execute Cross-Match", "Detect Discrepancies"]

            case = OperationalCase(
                case_id=case_id,
                cliente_id=cliente_id,
                job_id=job_id,
                skill_id=skill_id, # type: ignore
                demanda_original=str(demanda_original),
                hypothesis=hypothesis,
                taxonomia_pyme=payload.get("taxonomia_pyme") or {},
                variables_curadas=variables,
                evidencia_disponible=evidence,
                condiciones_validadas=payload.get("condiciones_validadas") or [],
                formula_applicable=payload.get("formula_applicable") or skill_id,
                pathology_possible=payload.get("pathology_possible"),
                referencias_necesarias=payload.get("referencias_necesarias") or [],
                investigation_plan=plan,
                status="OPEN",
            )

            # 6. Persistence
            operational_case_repository.create_case(case)

            return {
                "status": "OPERATIONAL_CASE_CREATED",
                "case_id": case_id,
                "job_id": job_id,
            }

        except ValueError as ve:
            return {
                "status": "REJECTED",
                "error_type": "INVALID_JOB_PAYLOAD",
                "reason": str(ve),
            }
        except Exception as e:
            return {
                "status": "REJECTED",
                "error_type": "INTERNAL_ERROR",
                "reason": str(e),
            }


def build_operational_case(
    cliente_id: str,
    job_id: str,
    job_repository: Any,
    operational_case_repository: Any,
) -> dict[str, Any]:
    return OperationalCaseOrchestrator().build_operational_case(
        cliente_id, job_id, job_repository, operational_case_repository
    )
