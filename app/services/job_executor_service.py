from __future__ import annotations

from typing import Any
from app.services.job_authorization_service import JobAuthorizationService
from app.orchestrator.models import Job, STATE_RUNNING


class JobExecutorService:
    """Service to execute authorized jobs."""

    def __init__(self, auth_service: JobAuthorizationService | None = None):
        self.auth_service = auth_service or JobAuthorizationService()

    def start_authorized_job(
        self,
        cliente_id: str,
        job_id: str,
        job_repository: Any,
        decision_repository: Any,
    ) -> dict[str, Any]:
        """Validates authorization and moves job to RUNNING state.
        
        Boundary: Minimal implementation - only state transition.
        """
        # 1. Check Authorization
        auth_res = self.auth_service.authorize_job_execution(
            cliente_id=cliente_id,
            job_id=job_id,
            job_repository=job_repository,
            decision_repository=decision_repository
        )

        if auth_res["status"] != "AUTHORIZED":
            return auth_res

        # 2. Transition State
        # Fetch data to reconstitute the Job object
        job_data = job_repository.get_job(job_id)
        if not job_data:
            return {"status": "INVALID_STATE", "reason": "JOB_NOT_FOUND"}

        # Create Job object and update state
        job = Job(
            job_id=job_data["job_id"],
            current_state=STATE_RUNNING,
            status="running",
            skill_id=job_data.get("skill_id"),
            payload=job_data.get("payload", {}),
            blocking_reason=None
        )

        # 3. Persist Change
        job_repository.save_job(job)

        return {
            "status": "JOB_STARTED",
            "job_id": job_id,
            "decision_id": auth_res["decision_id"]
        }
