from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Callable
from uuid import uuid4

from app.contracts.bem_runs import BemRunRecord
from app.repositories.bem_run_repository import BemRunRepository
from app.services.bem_client import BemClient
from app.services.bem_submit_port import BemSubmitPort


class BemSubmitService:
    def __init__(
        self,
        *,
        bem_client: BemClient | BemSubmitPort,
        bem_run_repository: BemRunRepository,
        now_provider: Callable[[], datetime] | None = None,
        run_id_provider: Callable[[], str] | None = None,
    ) -> None:
        self._bem_client = bem_client
        self._bem_run_repository = bem_run_repository
        self._now_provider = now_provider or (lambda: datetime.now(timezone.utc))
        self._run_id_provider = run_id_provider or (lambda: str(uuid4()))

    def submit(
        self,
        tenant_id: str,
        workflow_id: str,
        payload: dict[str, Any],
    ) -> BemRunRecord:
        _require_non_empty(tenant_id, "tenant_id")
        _require_non_empty(workflow_id, "workflow_id")
        if not isinstance(payload, dict) or not payload:
            raise ValueError("payload is required")

        run_id = self._run_id_provider()
        _require_non_empty(run_id, "run_id")
        created_at = _to_iso(self._now_provider())

        run = BemRunRecord(
            tenant_id=tenant_id.strip(),
            run_id=run_id.strip(),
            workflow_id=workflow_id.strip(),
            status="SUBMITTED",
            request_payload=payload,
            response_payload=None,
            created_at=created_at,
            updated_at=None,
            error_message=None,
        )
        self._bem_run_repository.create(run)

        try:
            response = self._submit_with_client(
                tenant_id=tenant_id.strip(),
                workflow_id=workflow_id.strip(),
                payload=payload,
            )
        except Exception as exc:
            failed_at = _to_iso(self._now_provider())
            self._bem_run_repository.mark_failed(
                tenant_id=tenant_id.strip(),
                run_id=run_id.strip(),
                error_message=str(exc),
                updated_at=failed_at,
            )
            raise

        completed_at = _to_iso(self._now_provider())
        self._bem_run_repository.mark_completed(
            tenant_id=tenant_id.strip(),
            run_id=run_id.strip(),
            response_payload=response,
            updated_at=completed_at,
        )
        updated = self._bem_run_repository.get_by_run_id(tenant_id.strip(), run_id.strip())
        if updated is None:
            raise RuntimeError("persisted run not found")
        return updated

    def _submit_with_client(
        self,
        *,
        tenant_id: str,
        workflow_id: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        try:
            return self._bem_client.submit_payload(  # type: ignore[attr-defined]
                tenant_id=tenant_id,
                workflow_id=workflow_id,
                payload=payload,
            )
        except TypeError:
            return self._bem_client.submit_payload(  # type: ignore[attr-defined]
                workflow_id=workflow_id,
                payload=payload,
            )


def _require_non_empty(value: str, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} is required")


def _to_iso(value: datetime) -> str:
    if not isinstance(value, datetime):
        raise TypeError("now_provider must return datetime")
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    else:
        value = value.astimezone(timezone.utc)
    return value.isoformat()
