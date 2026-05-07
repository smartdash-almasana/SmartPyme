from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.api import api_router
from app.laboratorio_pyme.p0_runner import LaboratorioP0Result


def create_app():
    app = FastAPI()
    app.include_router(api_router, prefix="/api/v1")
    return app


def test_create_caso_ok(monkeypatch):
    from app.api.v1.endpoints import laboratorio_p0

    def _fake_run(**kwargs):
        return LaboratorioP0Result(
            cliente_id="cliente_demo",
            case_id="case-1",
            job_id="job-1",
            report_id="rep-1",
            status="closed",
        )

    monkeypatch.setattr(laboratorio_p0, "run_laboratorio_p0", _fake_run)
    client = TestClient(create_app())
    payload = {
        "cliente_id": "cliente_demo",
        "dueno_nombre": "Dueño Demo",
        "laboratorio": "diagnostico_operativo",
        "hallazgo": "Primer hallazgo demo",
    }
    res = client.post("/api/v1/laboratorio/p0/casos", json=payload)
    assert res.status_code == 200
    assert res.json() == {
        "cliente_id": "cliente_demo",
        "case_id": "case-1",
        "job_id": "job-1",
        "report_id": "rep-1",
        "status": "closed",
    }


def test_create_caso_input_invalido_422():
    client = TestClient(create_app())
    res = client.post("/api/v1/laboratorio/p0/casos", json={"cliente_id": "x"})
    assert res.status_code == 422


def test_create_caso_error_sanitizado_sin_secret_leak(monkeypatch):
    from app.api.v1.endpoints import laboratorio_p0

    def _fake_run_error(**kwargs):
        raise RuntimeError(
            "SECRET_KEY_123 SMARTPYME_SUPABASE_KEY https://example.supabase.co"
        )

    monkeypatch.setattr(laboratorio_p0, "run_laboratorio_p0", _fake_run_error)
    client = TestClient(create_app())
    payload = {
        "cliente_id": "cliente_demo",
        "dueno_nombre": "Dueño Demo",
        "laboratorio": "diagnostico_operativo",
        "hallazgo": "Primer hallazgo demo",
    }
    res = client.post("/api/v1/laboratorio/p0/casos", json=payload)
    assert res.status_code == 400
    detail = res.json()["detail"]
    assert "SECRET_KEY_123" not in detail
    assert "SMARTPYME_SUPABASE_KEY" not in detail
    assert "supabase.co" not in detail
