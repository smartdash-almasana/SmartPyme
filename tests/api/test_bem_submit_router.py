from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.bem_submit_router import (
    get_bem_client,
    get_bem_runs_db_path,
    get_curated_evidence_db_path,
    get_run_id_provider,
    router,
)
from app.repositories.bem_run_repository import BemRunRepository
from app.repositories.curated_evidence_repository import CuratedEvidenceRepositoryBackend


class _FakeBemClientOk:
    """
    Fake BEM client con estructura real de response_payload.
    Devuelve outputs[0].transformedContent compatible con BemCuratedEvidenceAdapter.
    """
    def __init__(self) -> None:
        self.last_workflow_id: str | None = None
        self.last_payload: dict | None = None

    def submit_payload(self, workflow_id: str, payload: dict) -> dict:
        self.last_workflow_id = workflow_id
        self.last_payload = payload
        return {
            "callReferenceID": "call-ref-123",
            "callID": "call-123",
            "avgConfidence": 0.91,
            "inputType": "excel",
            "outputs": [
                {
                    "transformedContent": {
                        "producto": "Mouse Gamer RGB",
                        "precio_venta": 10,
                        "costo_unitario": 80,
                        "cantidad": 5,
                        "source_name": "ventas_demo.xlsx",
                        "source_type": "excel",
                    }
                }
            ],
        }


class _FakeBemClientBemResponse:
    """Devuelve response_payload con estructura real de BEM (outputs[0].transformedContent)."""

    def __init__(self, call_reference_id: str = "ref-router-001") -> None:
        self._call_reference_id = call_reference_id

    def submit_payload(self, workflow_id: str, payload: dict) -> dict:
        return {
            "callReferenceID": self._call_reference_id,
            "callID": "call-router-abc",
            "avgConfidence": 0.88,
            "inputType": "excel",
            "workflow_id": workflow_id,
            "outputs": [
                {
                    "transformedContent": {
                        "precio_venta": 10.0,
                        "costo_unitario": 80.0,
                        "source_name": "ventas.xlsx",
                        "source_type": "excel",
                    }
                }
            ],
        }


class _FakeBemClientFail:
    def submit_payload(self, workflow_id: str, payload: dict):
        raise RuntimeError("bem unavailable")


def _create_app(
    *,
    db_path: Path,
    bem_client,
    run_id: str = "run-test-001",
    curated_db_path: Path | None = None,
) -> FastAPI:
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_bem_runs_db_path] = lambda: db_path
    app.dependency_overrides[get_bem_client] = lambda: bem_client
    app.dependency_overrides[get_run_id_provider] = lambda: (lambda: run_id)
    if curated_db_path is not None:
        app.dependency_overrides[get_curated_evidence_db_path] = lambda: curated_db_path
    return app


def test_submit_exitoso(tmp_path: Path):
    db_path = tmp_path / "bem_runs.db"
    fake = _FakeBemClientBemResponse(call_reference_id="ref-ok-1")
    client = TestClient(_create_app(db_path=db_path, bem_client=fake, run_id="run-ok-1", curated_db_path=tmp_path / "curated.db"))

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
    client = TestClient(_create_app(db_path=db_path, bem_client=_FakeBemClientOk(), run_id="run-ok-2", curated_db_path=tmp_path / "curated.db"))

    client.post("/bem/submit", json={"tenant_id": "tenant-a", "workflow_id": "wf-1", "payload": {"x": 1}})
    run = BemRunRepository(db_path).get_by_run_id("tenant-a", "run-ok-2")

    assert run is not None
    assert run.status == "COMPLETED"
    assert run.response_payload is not None
    assert run.response_payload["callReferenceID"] == "call-ref-123"
    assert "outputs" in run.response_payload


def test_client_recibe_workflow_id_y_payload(tmp_path: Path):
    db_path = tmp_path / "bem_runs.db"
    fake = _FakeBemClientOk()
    client = TestClient(_create_app(db_path=db_path, bem_client=fake, run_id="run-ok-3", curated_db_path=tmp_path / "curated.db"))

    payload = {"price": 10, "cost": 80}
    client.post("/bem/submit", json={"tenant_id": "tenant-a", "workflow_id": "wf-xyz", "payload": payload})

    assert fake.last_workflow_id == "wf-xyz"
    assert fake.last_payload == payload


def test_tenant_vacio(tmp_path: Path):
    db_path = tmp_path / "bem_runs.db"
    client = TestClient(_create_app(db_path=db_path, bem_client=_FakeBemClientOk(), curated_db_path=tmp_path / "curated.db"))

    res = client.post("/bem/submit", json={"tenant_id": "", "workflow_id": "wf-1", "payload": {"x": 1}})

    assert res.status_code == 400
    assert "tenant_id" in res.json()["detail"]


def test_workflow_vacio(tmp_path: Path):
    db_path = tmp_path / "bem_runs.db"
    client = TestClient(_create_app(db_path=db_path, bem_client=_FakeBemClientOk(), curated_db_path=tmp_path / "curated.db"))

    res = client.post("/bem/submit", json={"tenant_id": "tenant-a", "workflow_id": "", "payload": {"x": 1}})

    assert res.status_code == 400
    assert "workflow_id" in res.json()["detail"]


def test_payload_vacio(tmp_path: Path):
    db_path = tmp_path / "bem_runs.db"
    client = TestClient(_create_app(db_path=db_path, bem_client=_FakeBemClientOk(), curated_db_path=tmp_path / "curated.db"))

    res = client.post("/bem/submit", json={"tenant_id": "tenant-a", "workflow_id": "wf-1", "payload": {}})

    assert res.status_code == 400
    assert "payload" in res.json()["detail"]


def test_falla_client_retorna_502(tmp_path: Path):
    db_path = tmp_path / "bem_runs.db"
    client = TestClient(_create_app(db_path=db_path, bem_client=_FakeBemClientFail(), run_id="run-f-1", curated_db_path=tmp_path / "curated.db"))

    res = client.post("/bem/submit", json={"tenant_id": "tenant-a", "workflow_id": "wf-1", "payload": {"x": 1}})

    assert res.status_code == 502
    assert "bem unavailable" in res.json()["detail"]


def test_falla_client_persiste_failed(tmp_path: Path):
    db_path = tmp_path / "bem_runs.db"
    client = TestClient(_create_app(db_path=db_path, bem_client=_FakeBemClientFail(), run_id="run-f-2", curated_db_path=tmp_path / "curated.db"))

    client.post("/bem/submit", json={"tenant_id": "tenant-a", "workflow_id": "wf-1", "payload": {"x": 1}})
    run = BemRunRepository(db_path).get_by_run_id("tenant-a", "run-f-2")

    assert run is not None
    assert run.status == "FAILED"
    assert run.error_message == "bem unavailable"


def test_run_id_deterministico_en_tests(tmp_path: Path):
    db_path = tmp_path / "bem_runs.db"
    client = TestClient(_create_app(db_path=db_path, bem_client=_FakeBemClientBemResponse(call_reference_id="ref-fixed"), run_id="run-fixed-999", curated_db_path=tmp_path / "curated.db"))

    res = client.post(
        "/bem/submit",
        json={"tenant_id": "tenant-a", "workflow_id": "wf-1", "payload": {"x": 1}},
    )

    assert res.status_code == 200
    assert res.json()["run_id"] == "run-fixed-999"


# ---------------------------------------------------------------------------
# Tests: curated evidence persiste via HTTP submit
# ---------------------------------------------------------------------------


def test_http_submit_completed_persiste_curated_evidence(tmp_path: Path) -> None:
    """COMPLETED via HTTP persiste run Y curated evidence."""
    db_path = tmp_path / "bem_runs.db"
    curated_db = tmp_path / "curated.db"
    client = TestClient(
        _create_app(
            db_path=db_path,
            bem_client=_FakeBemClientBemResponse(call_reference_id="ref-http-001"),
            run_id="run-http-001",
            curated_db_path=curated_db,
        )
    )

    res = client.post(
        "/bem/submit",
        json={"tenant_id": "tenant-http", "workflow_id": "wf-1", "payload": {"x": 1}},
    )

    assert res.status_code == 200
    assert res.json()["status"] == "COMPLETED"

    records = CuratedEvidenceRepositoryBackend(curated_db).list_by_tenant("tenant-http")
    assert len(records) == 1
    assert records[0].evidence_id == "ref-http-001"
    assert records[0].tenant_id == "tenant-http"
    assert records[0].payload["precio_venta"] == 10.0


def test_http_submit_tenant_id_preservado_en_curated_evidence(tmp_path: Path) -> None:
    """tenant_id del submit queda en el CuratedEvidenceRecord."""
    db_path = tmp_path / "bem_runs.db"
    curated_db = tmp_path / "curated.db"
    client = TestClient(
        _create_app(
            db_path=db_path,
            bem_client=_FakeBemClientBemResponse(call_reference_id="ref-tenant-http"),
            run_id="run-http-002",
            curated_db_path=curated_db,
        )
    )

    client.post(
        "/bem/submit",
        json={"tenant_id": "tenant-xyz-http", "workflow_id": "wf-1", "payload": {"x": 1}},
    )

    records = CuratedEvidenceRepositoryBackend(curated_db).list_by_tenant("tenant-xyz-http")
    assert len(records) == 1
    assert records[0].tenant_id == "tenant-xyz-http"
    # Tenant isolation
    assert CuratedEvidenceRepositoryBackend(curated_db).list_by_tenant("other-tenant") == []


def test_http_submit_bem_failure_no_persiste_curated_evidence(tmp_path: Path) -> None:
    """Si BEM falla, no se persiste curated evidence."""
    db_path = tmp_path / "bem_runs.db"
    curated_db = tmp_path / "curated.db"
    client = TestClient(
        _create_app(
            db_path=db_path,
            bem_client=_FakeBemClientFail(),
            run_id="run-http-fail",
            curated_db_path=curated_db,
        )
    )

    res = client.post(
        "/bem/submit",
        json={"tenant_id": "tenant-a", "workflow_id": "wf-1", "payload": {"x": 1}},
    )

    assert res.status_code == 502
    assert CuratedEvidenceRepositoryBackend(curated_db).list_by_tenant("tenant-a") == []
