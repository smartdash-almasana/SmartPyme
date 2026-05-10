"""
Smoke tests: rutas BEM y diagnóstico registradas en la app principal.

Verifica que los endpoints están montados bajo /api/v1 y responden
con los status codes esperados.

Aislamiento: monkeypatch resetea el singleton _default_repo en ambos
módulos de router apuntando a un SQLite temporal por test.
Sin tocar código productivo.
"""
from __future__ import annotations

import uuid
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import app.api.bem_webhook_router as _bem_mod
import app.api.diagnostic_router as _diag_mod
from app.main import app as main_app
from app.repositories.curated_evidence_repository import CuratedEvidenceRepositoryBackend


# ---------------------------------------------------------------------------
# Fixture: resetea singletons a DB temporal antes de cada test
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _isolated_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Reemplaza _default_repo en bem_webhook_router y diagnostic_router
    con una instancia fresca apuntando a un SQLite temporal.
    Garantiza aislamiento total entre tests y ejecuciones.
    """
    db = tmp_path / "smoke_test.db"
    fresh_repo = CuratedEvidenceRepositoryBackend(db_path=db)
    monkeypatch.setattr(_bem_mod, "_default_repo", fresh_repo)
    monkeypatch.setattr(_diag_mod, "_default_repo", fresh_repo)


@pytest.fixture()
def client() -> TestClient:
    return TestClient(main_app)


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _unique_evidence_id() -> str:
    return f"smoke-ev-{uuid.uuid4().hex[:8]}"


def _valid_bem_body(
    tenant_id: str = "smoke-tenant",
    evidence_id: str | None = None,
    precio_venta: float = 10.0,
    costo_unitario: float = 80.0,
) -> dict:
    return {
        "tenant_id": tenant_id,
        "payload": {
            "evidence_id": evidence_id or _unique_evidence_id(),
            "kind": "excel",
            "data": {"precio_venta": precio_venta, "costo_unitario": costo_unitario},
            "source": {"source_name": "smoke.xlsx", "source_type": "excel_file"},
        },
    }


# ---------------------------------------------------------------------------
# Rutas BEM montadas
# ---------------------------------------------------------------------------


def test_bem_webhook_route_mounted(client: TestClient) -> None:
    """POST /api/v1/webhooks/bem responde (no 404)."""
    res = client.post("/api/v1/webhooks/bem", json={})
    assert res.status_code == 400


def test_bem_webhook_valid_request_via_main_app(client: TestClient) -> None:
    """POST /api/v1/webhooks/bem con payload válido retorna 200."""
    ev_id = _unique_evidence_id()
    res = client.post("/api/v1/webhooks/bem", json=_valid_bem_body(evidence_id=ev_id))

    assert res.status_code == 200
    assert res.json()["status"] == "accepted"
    assert res.json()["tenant_id"] == "smoke-tenant"
    assert res.json()["evidence_id"] == ev_id


def test_bem_webhook_idempotent_different_ids(client: TestClient) -> None:
    """Dos POSTs con evidence_id distintos retornan 200 ambos."""
    res1 = client.post("/api/v1/webhooks/bem", json=_valid_bem_body())
    res2 = client.post("/api/v1/webhooks/bem", json=_valid_bem_body())

    assert res1.status_code == 200
    assert res2.status_code == 200


def test_bem_list_route_mounted(client: TestClient) -> None:
    """GET /api/v1/webhooks/bem/{tenant_id} responde (no 404)."""
    res = client.get("/api/v1/webhooks/bem/smoke-tenant")
    assert res.status_code == 200
    assert "items" in res.json()


def test_bem_list_reflects_posted_evidence(client: TestClient) -> None:
    """Evidencia posteada aparece en el listado del tenant."""
    ev_id = _unique_evidence_id()
    client.post("/api/v1/webhooks/bem", json=_valid_bem_body(evidence_id=ev_id))

    res = client.get("/api/v1/webhooks/bem/smoke-tenant")
    ids = [i["evidence_id"] for i in res.json()["items"]]
    assert ev_id in ids


def test_bem_detail_route_mounted_returns_404_when_empty(client: TestClient) -> None:
    """GET /api/v1/webhooks/bem/{tenant_id}/{evidence_id} retorna 404 si no existe."""
    res = client.get("/api/v1/webhooks/bem/smoke-tenant/ev-inexistente")
    assert res.status_code == 404


def test_bem_detail_route_returns_200_after_post(client: TestClient) -> None:
    """GET /api/v1/webhooks/bem/{tenant_id}/{evidence_id} retorna 200 tras POST."""
    ev_id = _unique_evidence_id()
    client.post("/api/v1/webhooks/bem", json=_valid_bem_body(evidence_id=ev_id))

    res = client.get(f"/api/v1/webhooks/bem/smoke-tenant/{ev_id}")
    assert res.status_code == 200
    assert res.json()["evidence_id"] == ev_id


# ---------------------------------------------------------------------------
# Rutas diagnóstico montadas
# ---------------------------------------------------------------------------


def test_diagnostico_route_mounted(client: TestClient) -> None:
    """GET /api/v1/diagnostico/{tenant_id} responde (no 404)."""
    res = client.get("/api/v1/diagnostico/smoke-tenant")
    assert res.status_code == 200
    assert "findings" in res.json()
    assert "evidence_count" in res.json()


def test_diagnostico_reflects_posted_evidence(client: TestClient) -> None:
    """Diagnóstico detecta VENTA_BAJO_COSTO en evidencia posteada."""
    client.post(
        "/api/v1/webhooks/bem",
        json=_valid_bem_body(precio_venta=5.0, costo_unitario=100.0),
    )

    res = client.get("/api/v1/diagnostico/smoke-tenant")
    assert res.status_code == 200
    types = [f["finding_type"] for f in res.json()["findings"]]
    assert "VENTA_BAJO_COSTO" in types


def test_diagnostico_informe_route_mounted(client: TestClient) -> None:
    """GET /api/v1/diagnostico/{tenant_id}/informe responde (no 404)."""
    res = client.get("/api/v1/diagnostico/smoke-tenant/informe")
    assert res.status_code == 200
    assert "text/markdown" in res.headers["content-type"]
    assert "# Diagnóstico Operacional" in res.text


def test_diagnostico_informe_contains_finding(client: TestClient) -> None:
    """Informe Markdown contiene VENTA_BAJO_COSTO tras POST."""
    client.post(
        "/api/v1/webhooks/bem",
        json=_valid_bem_body(precio_venta=5.0, costo_unitario=100.0),
    )

    res = client.get("/api/v1/diagnostico/smoke-tenant/informe")
    assert "VENTA_BAJO_COSTO" in res.text


def test_diagnostico_unknown_tenant_returns_empty(client: TestClient) -> None:
    """GET /api/v1/diagnostico/{tenant_id} para tenant inexistente retorna 200 vacío."""
    res = client.get("/api/v1/diagnostico/tenant-que-no-existe-smoke")
    assert res.status_code == 200
    assert res.json()["findings"] == []
    assert res.json()["evidence_count"] == 0


# ---------------------------------------------------------------------------
# Health no roto
# ---------------------------------------------------------------------------


def test_health_still_ok(client: TestClient) -> None:
    """El endpoint /health no fue afectado por el registro de nuevos routers."""
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


# ---------------------------------------------------------------------------
# Case-insensitive kind via main app
# ---------------------------------------------------------------------------


def test_bem_webhook_accepts_uppercase_kind_via_main_app(client: TestClient) -> None:
    """POST /api/v1/webhooks/bem acepta kind en mayúsculas."""
    body = _valid_bem_body()
    body["payload"]["kind"] = "EXCEL"

    res = client.post("/api/v1/webhooks/bem", json=body)

    assert res.status_code == 200
    assert res.json()["status"] == "accepted"
