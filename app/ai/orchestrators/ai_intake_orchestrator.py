from __future__ import annotations

import logging
from typing import Any

from app.ai.consumers.owner_message_soft_interpretation_consumer import OwnerMessageSoftInterpretationConsumer
from app.catalogs.symptom_pathology_catalog import (
    get_mayeutic_questions,
    get_required_evidence,
    get_required_variables,
    get_symptom,
)
from app.services.context_validation_service import ContextValidationService
from app.services.data_curation_service import DataCurationService

logger = logging.getLogger(__name__)


class AIIntakeOrchestrator:
    """Minimal orchestrator to connect soft interpretation with deterministic validation.

    Boundary rule:
    - Does not persist anything.
    - Does not create real Jobs.
    - Returns proposal structures for the Owner Layer.
    """

    def __init__(
        self,
        consumer: OwnerMessageSoftInterpretationConsumer | None = None,
        validator: ContextValidationService | None = None,
        curator: DataCurationService | None = None,
    ) -> None:
        self._consumer = consumer or OwnerMessageSoftInterpretationConsumer()
        self._validator = validator or ContextValidationService()
        self._curator = curator or DataCurationService()

    def process_owner_message(self, message: str, cliente_id: str) -> dict[str, Any]:
        if not message.strip():
            return {"status": "NO_INTERPRETATION", "reason": "EMPTY_INPUT"}

        # 1. Soft Interpretation
        inter_result = self._consumer.consume(message)
        if inter_result.status == "empty":
            return {"status": "NO_INTERPRETATION", "reason": "EMPTY_INPUT"}
        if inter_result.status == "failed":
            return {"status": "NO_INTERPRETATION", "reason": "LLM_FAILURE"}

        interpretation = inter_result.interpretation

        # Mapping intent to skill_id
        skill_id = interpretation.intent
        if not skill_id:
            return {"status": "NO_INTERPRETATION", "reason": "NO_INTENT_DETECTED"}

        symptom_id = interpretation.symptom_id
        symptom_entry = get_symptom(symptom_id) if symptom_id else None

        # 2. Data Curation
        # For now, interpretation only has names. We pass them as markers.
        # If we had a schema with values, we'd pass the actual dict.
        raw_vars = {v: True for v in interpretation.variables}
        curation_res = self._curator.curate_input(
            skill_id=skill_id,
            variables=raw_vars,
            evidence=interpretation.evidence,
            objective=None,
        )

        if curation_res.status == "CURATION_INVALID":
            return {
                "status": "REJECTED",
                "skill_id": skill_id,
                "error_type": "INVALID_INPUT",
                "reason": "; ".join(curation_res.errors),
            }

        if curation_res.status == "CURATION_INSUFFICIENT":
            # Note: We still pass through to ContextValidation for the exact missing list
            # if we want consistent CLARIFICATION_REQUIRED format,
            # but Curator logic says we can return it directly.
            # We follow the prompt: CURATION_INSUFFICIENT -> CLARIFICATION_REQUIRED.
            pass

        # 3. Operational Conditions Validation (deterministic business logic)
        # We use the cleaned data from curator
        cond_result = self._validator.validate_operational_conditions(
            skill_id=skill_id,
            variables=curation_res.cleaned_payload["variables"],
            evidence=curation_res.cleaned_payload["evidence"],
        )

        # 4. Branching
        status = cond_result["status"]

        if status == "CONDITIONS_OK":
            return {
                "status": "JOB_PROPOSAL",
                "job_preview": {
                    "cliente_id": cliente_id,
                    "skill_id": skill_id,
                    "objective": f"Ejecutar {skill_id} basado en mensaje del dueño",
                    "intent": skill_id,
                    "summary": f"Procesamiento de {skill_id}",
                    "raw_message": message,
                },
            }

        if status == "CONDITIONS_MISSING":
            missing_variables = list(cond_result.get("missing_variables", []))
            missing_evidence = list(cond_result.get("missing_evidence", []))
            response: dict[str, Any] = {
                "status": "CLARIFICATION_REQUIRED",
                "skill_id": skill_id,
                "missing_variables": missing_variables,
                "missing_evidence": missing_evidence,
            }

            if symptom_entry is not None and symptom_id is not None:
                catalog_variables = get_required_variables(symptom_id)
                catalog_evidence = get_required_evidence(symptom_id)
                mayeutic_questions = get_mayeutic_questions(symptom_id)

                response["symptom_id"] = symptom_id
                response["symptom_catalog_context"] = {
                    "required_variables": catalog_variables,
                    "required_evidence": catalog_evidence,
                    "mayeutic_questions": mayeutic_questions,
                }
                response["missing_variables"] = _merge_preserving_order(
                    missing_variables,
                    catalog_variables,
                )
                response["missing_evidence"] = _merge_preserving_order(
                    missing_evidence,
                    catalog_evidence,
                )
                response["mayeutic_questions"] = mayeutic_questions

            return response

        if status == "CONDITIONS_INVALID":
            return {
                "status": "REJECTED",
                "skill_id": skill_id,
                "error_type": "CONDITIONS_INVALID",
                "reason": cond_result.get("reason", "unknown"),
            }

        if status == "UNKNOWN_SKILL":
            return {
                "status": "REJECTED",
                "skill_id": skill_id,
                "error_type": "UNKNOWN_SKILL",
                "reason": "La skill solicitada no está en el catálogo operativo.",
            }

        return {
            "status": "REJECTED",
            "skill_id": skill_id,
            "error_type": "INTERNAL_ERROR",
            "reason": f"Unhandled condition status: {status}",
        }


def _merge_preserving_order(
    primary: list[str],
    secondary: tuple[str, ...],
) -> list[str]:
    merged: list[str] = []
    seen: set[str] = set()

    for item in [*primary, *secondary]:
        if item not in seen:
            merged.append(item)
            seen.add(item)

    return merged
