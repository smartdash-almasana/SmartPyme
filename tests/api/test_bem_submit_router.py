from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.bem_submit_router import (
    get_bem_client,
    get_bem_runs_db_path,
    get_run_id_provider,
    router,
)
from app.repositories.bem_run_repository import BemRunRepository


class _FakeBemClientOk:
    def __init__(self) -> None:
        self.last_workflow_id: str | None = None
        self.last_payload: dict | None = None

    def submit_payload(self, workflow_id: str, payload: dict):
        self.last_workflow_id = workflow_id
        self.last_payload = payload
        return {"accepted": True, "provider_run_id": "bem-123"}


class _FakeBemClientFail:
    def submit_payload(self, workflow_id: str, payload: dict):
        raise RuntimeError("bem unavailable")


def _create_app(
    *,
    db_path: Path,
    bem_client,
    run_id: str = "run-test-001",
) -> FastAPI:
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_bem_runs_db_path] = lambda: db_path
    app.dependency_overrides[get_bem_client] = lambda: bem_client
    app.dependency_overrides[get_run_id_provider] = lambda: (lambda: run_id)
    return app


def test_submit_exitoso(tmp_path: Path):
    db_path = tmp_path / "bem_runs.db"
    fake = _FakeBemClientOk()
    client = TestClient(_create_app(db_path=db_path, bem_client=fake, run_id="run-ok-1"))

    res = client.post(
        "/bem/submit",
        json={"tenant_id": "tenant-a", "workflow_id": "wf-1", "payload": {"x": 1}},
    )

    assert res.status_code == 200
    assert res.json() == {
        "tenant_id": "tenant-a",
        "run_id": "run-ok-1",
        "workflow_id": "wf-1",
        "status": "COMPLETED",
    }


def test_run_persistido_completed(tmp_path: Path):
    db_path = tmp_path / "bem_runs.db"
    client = TestClient(_create_app(db_path=db_path, bem_client=_FakeBemClientOk(), run_id="run-ok-2"))

    client.post("/bem/submit", json={"tenant_id": "tenant-a", "workflow_id": "wf-1", "payload": {"x": 1}})
    run = BemRunRepository(db_path).get_by_run_id("tenant-a", "run-ok-2")

    assert run is not None
    assert run.status == "COMPLETED"
    assert run.response_payload == {"accepted": True, "provider_run_id": "bem-123"}


def test_client_recibe_workflow_id_y_payload(tmp_path: Path):
    db_path = tmp_path / "bem_runs.db"
    fake = _FakeBemClientOk()
    client = TestClient(_create_app(db_path=db_path, bem_client=fake, run_id="run-ok-3"))

    payload = {"price": 10, "cost": 80}
    client.post("/bem/submit", json={"tenant_id": "tenant-a", "workflow_id": "wf-xyz", "payload": payload})

    assert fake.last_workflow_id == "wf-xyz"
    assert fake.last_payload == payload


def test_tenant_vacio(tmp_path: Path):
    db_path = tmp_path / "bem_runs.db"
    client = TestClient(_create_app(db_path=db_path, bem_client=_FakeBemClientOk()))

    res = client.post("/bem/submit", json={"tenant_id": "", "workflow_id": "wf-1", "payload": {"x": 1}})

    assert res.status_code == 400
    assert "tenant_id" in res.json()["detail"]


def test_workflow_vacio(tmp_path: Path):
    db_path = tmp_path / "bem_runs.db"
    client = TestClient(_create_app(db_path=db_path, bem_client=_FakeBemClientOk()))

    res = client.post("/bem/submit", json={"tenant_id": "tenant-a", "workflow_id": "", "payload": {"x": 1}})

    assert res.status_code == 400
    assert "workflow_id" in res.json()["detail"]


def test_payload_vacio(tmp_path: Path):
    db_path = tmp_path / "bem_runs.db"
    client = TestClient(_create_app(db_path=db_path, bem_client=_FakeBemClientOk()))

    res = client.post("/bem/submit", json={"tenant_id": "tenant-a", "workflow_id": "wf-1", "payload": {}})

    assert res.status_code == 400
    assert "payload" in res.json()["detail"]


def test_falla_client_retorna_502(tmp_path: Path):
    db_path = tmp_path / "bem_runs.db"
    client = TestClient(_create_app(db_path=db_path, bem_client=_FakeBemClientFail(), run_id="run-f-1"))

    res = client.post("/bem/submit", json={"tenant_id": "tenant-a", "workflow_id": "wf-1", "payload": {"x": 1}})

    assert res.status_code == 502
    assert "bem unavailable" in res.json()["detail"]


def test_falla_client_persiste_failed(tmp_path: Path):
    db_path = tmp_path / "bem_runs.db"
    client = TestClient(_create_app(db_path=db_path, bem_client=_FakeBemClientFail(), run_id="run-f-2"))

    client.post("/bem/submit", json={"tenant_id": "tenant-a", "workflow_id": "wf-1", "payload": {"x": 1}})
    run = BemRunRepository(db_path).get_by_run_id("tenant-a", "run-f-2")

    assert run is not None
    assert run.status == "FAILED"
    assert run.error_message == "bem unavailable"


def test_run_id_deterministico_en_tests(tmp_path: Path):
    db_path = tmp_path / "bem_runs.db"
    client = TestClient(_create_app(db_path=db_path, bem_client=_FakeBemClientOk(), run_id="run-fixed-999"))

    res = client.post(
        "/bem/submit",
        json={"tenant_id": "tenant-a", "workflow_id": "wf-1", "payload": {"x": 1}},
    )

    assert res.status_code == 200
    assert res.json()["run_id"] == "run-fixed-999"
