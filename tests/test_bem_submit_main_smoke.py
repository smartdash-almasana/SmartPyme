from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient

import app.api.bem_webhook_router as bem_webhook_router
import app.api.diagnostic_router as diagnostic_router
from app.api.bem_submit_router import (
    get_bem_client,
    get_bem_runs_db_path,
    get_run_id_provider,
)
from app.main import app
from app.repositories.curated_evidence_repository import CuratedEvidenceRepositoryBackend
from app.repositories.bem_run_repository import BemRunRepository


class _FakeBemClientOk:
    def submit_payload(self, workflow_id: str, payload: dict):
        return {"accepted": True, "provider_run_id": "bem-main-ok"}


class _FakeBemClientFail:
    def submit_payload(self, workflow_id: str, payload: dict):
        raise RuntimeError("bem down")


def _valid_webhook_body(*, evidence_id: str) -> dict:
    return {
        "tenant_id": "tenant-main",
        "payload": {
            "evidence_id": evidence_id,
            "kind": "EXCEL",
            "data": {"precio_venta": 10, "costo_unitario": 80},
            "source": {"source_name": "ventas.xlsx", "source_type": "excel"},
        },
    }


def test_main_app_bem_submit_success_and_routes_alive(tmp_path: Path, monkeypatch):
    db_path = tmp_path / "bem_runs.db"
    curated_db_path = tmp_path / "curated_evidence.db"
    isolated_repo = CuratedEvidenceRepositoryBackend(db_path=curated_db_path)
    monkeypatch.setattr(bem_webhook_router, "_default_repo", isolated_repo)
    monkeypatch.setattr(diagnostic_router, "_default_repo", isolated_repo)

    app.dependency_overrides[get_bem_runs_db_path] = lambda: db_path
    app.dependency_overrides[get_bem_client] = lambda: _FakeBemClientOk()
    app.dependency_overrides[get_run_id_provider] = lambda: (lambda: "run-main-001")
    client = TestClient(app)

    res_submit = client.post(
        "/api/v1/bem/submit",
        json={"tenant_id": "tenant-main", "workflow_id": "wf-main", "payload": {"x": 1}},
    )
    assert res_submit.status_code == 200
    assert res_submit.json() == {
        "tenant_id": "tenant-main",
        "run_id": "run-main-001",
        "workflow_id": "wf-main",
        "status": "COMPLETED",
    }

    run = BemRunRepository(db_path).get_by_run_id("tenant-main", "run-main-001")
    assert run is not None
    assert run.status == "COMPLETED"

    res_health = client.get("/health")
    assert res_health.status_code == 200
    assert res_health.json() == {"status": "ok"}

    evidence_id = f"ev-main-{uuid4()}"
    res_webhook = client.post("/api/v1/webhooks/bem", json=_valid_webhook_body(evidence_id=evidence_id))
    assert res_webhook.status_code == 200

    res_diag = client.get("/api/v1/diagnostico/tenant-main")
    assert res_diag.status_code == 200

    app.dependency_overrides.clear()


def test_main_app_bem_submit_client_failure_returns_502_and_persists_failed(tmp_path: Path):
    db_path = tmp_path / "bem_runs.db"
    app.dependency_overrides[get_bem_runs_db_path] = lambda: db_path
    app.dependency_overrides[get_bem_client] = lambda: _FakeBemClientFail()
    app.dependency_overrides[get_run_id_provider] = lambda: (lambda: "run-main-fail-001")
    client = TestClient(app)

    res_submit = client.post(
        "/api/v1/bem/submit",
        json={"tenant_id": "tenant-main", "workflow_id": "wf-main", "payload": {"x": 1}},
    )
    assert res_submit.status_code == 502
    assert "bem down" in res_submit.json()["detail"]

    run = BemRunRepository(db_path).get_by_run_id("tenant-main", "run-main-fail-001")
    assert run is not None
    assert run.status == "FAILED"

    app.dependency_overrides.clear()
