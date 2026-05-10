from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException

from app.repositories.bem_run_repository import BemRunRepository
from app.services.bem_client import BemClient
from app.services.bem_submit_service import BemSubmitService

router = APIRouter()


def get_bem_runs_db_path() -> Path:
    return Path(os.getenv("SMARTPYME_BEM_RUNS_DB_PATH", "data/bem_runs.db"))


def get_bem_client() -> BemClient:
    return BemClient()


def get_now_provider() -> Callable[[], datetime]:
    return lambda: datetime.now(timezone.utc)


def get_run_id_provider() -> Callable[[], str]:
    return lambda: str(uuid4())


def get_bem_submit_service(
    db_path: Path = Depends(get_bem_runs_db_path),
    bem_client: BemClient = Depends(get_bem_client),
    now_provider: Callable[[], datetime] = Depends(get_now_provider),
    run_id_provider: Callable[[], str] = Depends(get_run_id_provider),
) -> BemSubmitService:
    repo = BemRunRepository(db_path)
    return BemSubmitService(
        bem_client=bem_client,
        bem_run_repository=repo,
        now_provider=now_provider,
        run_id_provider=run_id_provider,
    )


@router.post("/bem/submit")
def submit_bem(
    body: dict[str, Any],
    service: BemSubmitService = Depends(get_bem_submit_service),
) -> dict[str, str]:
    tenant_id = body.get("tenant_id")
    workflow_id = body.get("workflow_id")
    payload = body.get("payload")

    if not isinstance(tenant_id, str) or not tenant_id.strip():
        raise HTTPException(status_code=400, detail="tenant_id is required")
    if not isinstance(workflow_id, str) or not workflow_id.strip():
        raise HTTPException(status_code=400, detail="workflow_id is required")
    if not isinstance(payload, dict) or not payload:
        raise HTTPException(status_code=400, detail="payload is required")

    try:
        run = service.submit(tenant_id=tenant_id, workflow_id=workflow_id, payload=payload)
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except (ValueError, TypeError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "tenant_id": run.tenant_id,
        "run_id": run.run_id,
        "workflow_id": run.workflow_id,
        "status": run.status,
    }
