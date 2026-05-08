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


# ---------------------------------------------------------------------------
# Tests GET /reportes/{report_id}
# ---------------------------------------------------------------------------

class _FakeReport:
    """Fake report para tests sin red."""
    def __init__(self, cliente_id, report_id, case_id="case-1", status="closed"):
        self.cliente_id = cliente_id
        self.report_id = report_id
        self.case_id = case_id
        self.diagnosis_status = status
        self.payload = {"hypothesis": "test", "findings": []}
        self.result = None
        self.metadata = {}


class _FakeReportRepo:
    def __init__(self, report=None):
        self._report = report

    def get_report(self, report_id: str):
        if self._report and self._report.report_id == report_id:
            return self._report
        return None


class _FakePersistenceContext:
    def __init__(self, report=None):
        self.reports = _FakeReportRepo(report)


def test_get_reporte_ok(monkeypatch):
    """GET /reportes/{report_id} retorna 200 con datos del report."""
    from app.laboratorio_pyme import persistence as persistence_mod

    fake_report = _FakeReport(
        cliente_id="cliente_demo",
        report_id="rep-1",
        case_id="case-1",
        status="closed",
    )

    def _fake_from_factory(**kwargs):
        return _FakePersistenceContext(report=fake_report)

    monkeypatch.setattr(
        persistence_mod.LaboratorioPersistenceContext,
        "from_repository_factory",
        staticmethod(_fake_from_factory),
    )

    client = TestClient(create_app())
    res = client.get("/api/v1/laboratorio/p0/reportes/rep-1?cliente_id=cliente_demo")
    assert res.status_code == 200
    data = res.json()
    assert data["cliente_id"] == "cliente_demo"
    assert data["report_id"] == "rep-1"
    assert data["case_id"] == "case-1"
    assert data["status"] == "closed"


def test_get_reporte_404_si_no_existe(monkeypatch):
    """GET /reportes/{report_id} retorna 404 si el report no existe."""
    from app.laboratorio_pyme import persistence as persistence_mod

    def _fake_from_factory(**kwargs):
        return _FakePersistenceContext(report=None)

    monkeypatch.setattr(
        persistence_mod.LaboratorioPersistenceContext,
        "from_repository_factory",
        staticmethod(_fake_from_factory),
    )

    client = TestClient(create_app())
    res = client.get("/api/v1/laboratorio/p0/reportes/no-existe?cliente_id=cliente_demo")
    assert res.status_code == 404


def test_get_reporte_no_expone_secrets_en_error(monkeypatch):
    """El 404 no expone secrets ni URLs de Supabase."""
    from app.laboratorio_pyme import persistence as persistence_mod

    def _fake_from_factory(**kwargs):
        return _FakePersistenceContext(report=None)

    monkeypatch.setattr(
        persistence_mod.LaboratorioPersistenceContext,
        "from_repository_factory",
        staticmethod(_fake_from_factory),
    )

    client = TestClient(create_app())
    res = client.get("/api/v1/laboratorio/p0/reportes/no-existe?cliente_id=cliente_demo")
    detail = res.json().get("detail", "")
    assert "supabase.co" not in detail
    assert "service_role" not in detail
    assert "SMARTPYME_SUPABASE" not in detail


def test_get_reporte_llama_load_env_local(monkeypatch):
    """GET /reportes/{report_id} llama load_env_local_if_exists antes de resolver provider."""
    from app.api.v1.endpoints import laboratorio_p0
    from app.laboratorio_pyme import persistence as persistence_mod

    called = []

    def _fake_load_env():
        called.append(True)

    def _fake_from_factory(**kwargs):
        return _FakePersistenceContext(report=_FakeReport(
            cliente_id="cliente_demo",
            report_id="rep-env-1",
        ))

    monkeypatch.setattr(laboratorio_p0, "load_env_local_if_exists", _fake_load_env)
    monkeypatch.setattr(
        persistence_mod.LaboratorioPersistenceContext,
        "from_repository_factory",
        staticmethod(_fake_from_factory),
    )

    client = TestClient(create_app())
    res = client.get("/api/v1/laboratorio/p0/reportes/rep-env-1?cliente_id=cliente_demo")
    assert res.status_code == 200
    assert called, "load_env_local_if_exists debe ser llamada en el endpoint GET reporte"


def test_form_contiene_consultar_reporte():
    """El HTML del formulario contiene el texto 'Consultar reporte'."""
    client = TestClient(create_app())
    res = client.get("/api/v1/laboratorio/p0/form")
    assert res.status_code == 200
    body = res.text
    assert "Consultar reporte" in body
    assert "/api/v1/laboratorio/p0/reportes/" in body


def test_form_contiene_reporte_confirmado():
    """El HTML del formulario contiene el texto 'Reporte confirmado' (report card)."""
    client = TestClient(create_app())
    res = client.get("/api/v1/laboratorio/p0/form")
    assert res.status_code == 200
    body = res.text
    assert "Reporte confirmado" in body


def test_form_contiene_datos_tecnicos():
    """El HTML del formulario contiene el texto 'Datos técnicos' (collapsible section)."""
    client = TestClient(create_app())
    res = client.get("/api/v1/laboratorio/p0/form")
    assert res.status_code == 200
    body = res.text
    assert "Datos técnicos" in body
