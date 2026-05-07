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


def test_health_ok():
    """GET /health retorna 200 y {"status": "ok"}."""
    from app.main import app as main_app

    client = TestClient(main_app)
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


def test_p0_endpoint_montado_en_main_app(monkeypatch):
    """POST /api/v1/laboratorio/p0/casos está montado en la app principal."""
    from app.api.v1.endpoints import laboratorio_p0
    from app.main import app as main_app

    def _fake_run(**kwargs):
        return LaboratorioP0Result(
            cliente_id="cliente_demo",
            case_id="case-main-1",
            job_id="job-main-1",
            report_id="rep-main-1",
            status="closed",
        )

    monkeypatch.setattr(laboratorio_p0, "run_laboratorio_p0", _fake_run)
    client = TestClient(main_app)
    payload = {
        "cliente_id": "cliente_demo",
        "dueno_nombre": "Dueño Demo",
        "laboratorio": "diagnostico_operativo",
        "hallazgo": "Primer hallazgo demo",
    }
    res = client.post("/api/v1/laboratorio/p0/casos", json=payload)
    assert res.status_code == 200
    assert res.json()["status"] == "closed"
    assert res.json()["case_id"] == "case-main-1"


def test_form_get_devuelve_html():
    """GET /api/v1/laboratorio/p0/form devuelve 200 con HTML del formulario."""
    client = TestClient(create_app())
    res = client.get("/api/v1/laboratorio/p0/form")
    assert res.status_code == 200
    assert "text/html" in res.headers["content-type"]
    body = res.text
    assert "Laboratorio" in body
    assert "cliente_id" in body
    assert "dueno_nombre" in body
    assert "laboratorio" in body
    assert "hallazgo" in body
    assert "/api/v1/laboratorio/p0/casos" in body


def test_form_no_expone_secrets():
    """El HTML del formulario no contiene referencias a secrets o URLs de Supabase."""
    client = TestClient(create_app())
    res = client.get("/api/v1/laboratorio/p0/form")
    body = res.text
    assert "supabase.co" not in body
    assert "service_role" not in body
    assert "SMARTPYME_SUPABASE" not in body
