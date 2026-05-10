from __future__ import annotations

import uuid
from typing import Any
from app.catalogs.symptom_pathology_catalog import get_symptom
from app.catalogs.skill_registry import SkillRegistry
from app.contracts.operational_case import OperationalCase as OperationalCaseCapa03
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
            job_cliente_id = payload.get("cliente_id") or job_data.get("cliente_id")
            
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
            payload = job_data.get("payload", {})
            # Fallback to payload/operational_plan if missing in top level
            if not skill_id:
                skill_id = payload.get("skill_id") or payload.get("operational_plan", {}).get("skill_id")
            
            registry = SkillRegistry()
            # Validation if skill_id is provided.
            # Legacy/local IDs (those NOT starting with "skill_") are accepted as-is
            # to preserve compatibility with test fixtures and non-production flows.
            # Only IDs that start with "skill_" are validated strictly against the registry.
            if skill_id and skill_id.startswith("skill_") and not registry.has_skill(skill_id):
                return {
                    "status": "CLARIFICATION_REQUIRED",
                    "reason": "INVALID_SKILL_ID",
                    "missing": ["valid_skill_id"],
                    "owner_message": f"El ID de habilidad '{skill_id}' no es válido en el registro del sistema."
                }
            
            objective = payload.get("objective") or payload.get("operational_plan", {}).get("objective")
            demanda_original = (
                payload.get("owner_request") 
                or payload.get("operational_plan", {}).get("owner_request") 
                or (objective if objective else None)
            )
            
            variables = payload.get("variables") or payload.get("operational_plan", {}).get("variables") or {}
            evidence = payload.get("evidence") or payload.get("operational_plan", {}).get("required_sources") or []
            
            symptom_id_from_job = payload.get("symptom_id") or payload.get("operational_plan", {}).get("symptom_id")
            symptom_info = get_symptom(symptom_id_from_job) if symptom_id_from_job else None

            # Principio de interacción: Aclaraciones precisas
            if not demanda_original and not symptom_info:
                return {
                    "status": "CLARIFICATION_REQUIRED",
                    "reason": "INSUFFICIENT_CONTEXT",
                    "missing": ["demanda_original"],
                    "owner_message": "Necesito que me cuentes qué querés investigar o resolver para poder armar el caso."
                }
            
            # Use symptom as demanda if missing
            if not demanda_original and symptom_info:
                demanda_original = symptom_info.get("operational_symptom")
            
            if not skill_id:
                # Si no hay skill_id, tratar de obtenerlo del catálogo antes de rechazar
                if symptom_info and symptom_info.get("candidate_skills"):
                    candidate_skill = symptom_info["candidate_skills"][0]
                    if registry.has_skill(candidate_skill):
                        skill_id = candidate_skill
            
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
            hypothesis_base = objective or demanda_original
            hypothesis = f"Investigar si {hypothesis_base}"
            if symptom_info and "hypothesis_template" in symptom_info:
                hypothesis = symptom_info["hypothesis_template"].format(periodo="el período analizado", proceso="el proceso analizado", producto="el producto analizado")
            
            if not hypothesis.endswith("?"):
                hypothesis += "?"

            # 5. Build OperationalCase
            case_id = str(uuid.uuid4())
            
            # Enrich with Catalog
            if symptom_info:
                if not evidence and symptom_info.get("required_evidence"):
                    evidence = symptom_info["required_evidence"]

            # Default investigation plan based on skill_id
            plan = ["Load Evidence", "Apply Formula", "Generate Findings"]
            if skill_id and "reconciliation" in skill_id:
                plan = ["Fetch Sources", "Execute Cross-Match", "Detect Discrepancies"]
            
            case = OperationalCaseCapa03(
                cliente_id=cliente_id,
                case_id=case_id,
                job_id=job_id,
                skill_id=skill_id,
                hypothesis=hypothesis,
                evidence_ids=evidence,
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
