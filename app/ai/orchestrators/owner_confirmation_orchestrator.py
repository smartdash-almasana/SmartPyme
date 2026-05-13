from __future__ import annotations

import uuid
from typing import Any, Literal, TypedDict

from app.contracts.execution_guard import enforce_execution_contract
from app.orchestrator.models import STATE_CREATED, Job
from app.orchestrator.persistence import save_job
from app.services.context_validation_service import ContextValidationService
from app.services.data_curation_service import DataCurationService


class OwnerConfirmationOverrides(TypedDict, total=False):
    objective: str | None
    variables: dict[str, Any] | None
    evidence: list[str] | None


class OwnerConfirmationInput(TypedDict):
    cliente_id: str
    skill_id: str
    action: Literal["CONFIRM", "REJECT"]
    overrides: OwnerConfirmationOverrides


class OwnerConfirmationOrchestrator:
    """Orchestrator to handle owner's confirmation/rejection of a proposed Job.

    Boundary rule:
    - Strictly validates input via Curator and Conditions.
    - Persists the Job only if action is CONFIRM and data is OK.
    - Ensures no IA metadata leaks into the real Job payload.
    """

    def __init__(
        self,
        curator: DataCurationService | None = None,
        validator: ContextValidationService | None = None,
    ) -> None:
        self._curator = curator or DataCurationService()
        self._validator = validator or ContextValidationService()

    def confirm_job(self, input_data: OwnerConfirmationInput) -> dict[str, Any]:
        cliente_id = input_data.get("cliente_id")
        skill_id = input_data.get("skill_id")
        action = input_data.get("action")
        overrides = input_data.get("overrides") or {}

        if not cliente_id or not skill_id:
            return {
                "status": "REJECTED",
                "skill_id": skill_id,
                "error_type": "INVALID_INPUT",
                "reason": "Missing cliente_id or skill_id",
            }

        if action == "REJECT":
            return {"status": "REJECT_ACKNOWLEDGED"}

        if action != "CONFIRM":
            return {
                "status": "REJECTED",
                "skill_id": skill_id,
                "error_type": "INVALID_INPUT",
                "reason": f"Invalid action: {action}",
            }

        try:
            enforce_execution_contract(
                dict(input_data),
                context="confirm_job.input",
                required_fields=("cliente_id", "skill_id", "action"),
            )
        except ValueError as ve:
            return {
                "status": "REJECTED",
                "skill_id": skill_id,
                "error_type": "INVALID_JOB_PAYLOAD",
                "reason": str(ve),
            }

        # 1. Data Curation (Technical Hygiene)
        curation_res = self._curator.curate_input(
            skill_id=skill_id,
            variables=overrides.get("variables") or {},
            evidence=overrides.get("evidence") or [],
            objective=overrides.get("objective"),
        )

        if curation_res.status == "CURATION_INVALID":
            return {
                "status": "REJECTED",
                "skill_id": skill_id,
                "error_type": "INVALID_INPUT",
                "reason": "; ".join(curation_res.errors),
            }

        # 2. Operational Conditions Validation (Business Logic)
        cond_result = self._validator.validate_operational_conditions(
            skill_id=skill_id,
            variables=curation_res.cleaned_payload["variables"],
            evidence=curation_res.cleaned_payload["evidence"],
        )

        if cond_result["status"] == "CONDITIONS_MISSING":
            return {
                "status": "CLARIFICATION_REQUIRED",
                "skill_id": skill_id,
                "missing_variables": cond_result.get("missing_variables", []),
                "missing_evidence": cond_result.get("missing_evidence", []),
            }

        if cond_result["status"] != "CONDITIONS_OK":
            return {
                "status": "REJECTED",
                "skill_id": skill_id,
                "error_type": "CONDITIONS_INVALID",
                "reason": f"Validation failed: {cond_result['status']}",
            }

        # 3. Persistence of real Job
        job_id = f"job-{uuid.uuid4().hex[:12]}"

        # Clean payload: strictly the sanitized and curated data
        payload = {
            "objective": curation_res.cleaned_payload["objective"],
            "variables": curation_res.cleaned_payload["variables"],
            "evidence": curation_res.cleaned_payload["evidence"],
            "cliente_id": cliente_id,
        }

        job = Job(
            job_id=job_id,
            current_state=STATE_CREATED,
            status="created",
            skill_id=skill_id,
            payload=payload,
        )

        try:
            enforce_execution_contract(
                job,
                context="confirm_job.job",
                required_fields=("job_id", "current_state", "payload"),
            )
        except ValueError as ve:
            return {
                "status": "REJECTED",
                "skill_id": skill_id,
                "error_type": "INVALID_JOB_PAYLOAD",
                "reason": str(ve),
            }

        try:
            save_job(job)
        except Exception as e:
            return {
                "status": "REJECTED",
                "skill_id": skill_id,
                "error_type": "INTERNAL_ERROR",
                "reason": f"Persistence failed: {str(e)}",
            }

        return {"status": "JOB_CREATED", "job_id": job_id}
