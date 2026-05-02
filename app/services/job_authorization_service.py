from __future__ import annotations

from typing import Any


class JobAuthorizationService:
    """Service to authorize job execution based on owner decisions."""

    def authorize_job_execution(
        self,
        cliente_id: str,
        job_id: str,
        job_repository: Any,
        decision_repository: Any,
    ) -> dict[str, Any]:
        """Verifies if a job is authorized to move to execution.
        
        Rules:
        - Job must exist.
        - Job must belong to the requesting cliente_id.
        - Job must be in 'created' or 'pending_owner_confirmation' status.
        - A DecisionRecord of type 'EJECUTAR' must exist for this job_id and cliente_id.
        """
        # 1. Fetch Job
        job_data = job_repository.get_job(job_id)
        if not job_data:
            return {"status": "INVALID_STATE", "reason": "JOB_NOT_FOUND"}

        # 2. Verify Client Isolation
        # Usually cliente_id is inside the payload's operational_plan
        payload = job_data.get("payload", {})
        op_plan = payload.get("operational_plan", {})
        job_cliente_id = op_plan.get("cliente_id")

        if job_cliente_id != cliente_id:
            return {"status": "INVALID_STATE", "reason": "JOB_NOT_FOUND"}

        # 3. Verify Job State
        status = job_data.get("status", "").lower()
        if status in ("running",):
            return {"status": "INVALID_STATE", "reason": "JOB_ALREADY_RUNNING"}
        if status in ("completed", "failed", "finished"):
            return {"status": "INVALID_STATE", "reason": "JOB_FINISHED"}

        if status not in ("created", "pending_owner_confirmation"):
            return {"status": "INVALID_STATE", "reason": "JOB_INVALID_STATE"}

        # 4. Fetch Decisions and find authorization
        # DecisionRepository is already initialized for the specific cliente_id
        decisions = decision_repository.list_by_cliente()

        target_decision = None
        for dec in decisions:
            if dec.job_id == job_id and dec.tipo_decision == "EJECUTAR":
                target_decision = dec
                break

        if not target_decision:
            # Check for non-EJECUTAR decisions to provide better context if needed
            # but per prompt, we just return NOT_AUTHORIZED
            return {"status": "NOT_AUTHORIZED", "reason": "MISSING_DECISION"}

        return {
            "status": "AUTHORIZED",
            "job_id": job_id,
            "decision_id": target_decision.decision_id,
        }
