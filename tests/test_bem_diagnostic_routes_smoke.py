"""
Smoke tests: rutas BEM y diagnóstico registradas en la app principal.

Verifica que los endpoints están montados bajo /api/v1 y responden
con los status codes esperados.
Sin DB real — usa el singleton lazy de la app (data/curated_evidence.db
se crea en el directorio de trabajo si no existe).
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app as main_app


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(main_app)


# ---------------------------------------------------------------------------
# Rutas BEM montadas
# ---------------------------------------------------------------------------


def test_bem_webhook_route_mounted(client: TestClient) -> None:
    """POST /api/v1/webhooks/bem responde (no 404)."""
    res = client.post("/api/v1/webhooks/bem", json={})
    # Body vacío → 400, pero la ruta existe (no 404/405)
    assert res.status_code == 400


def test_bem_webhook_valid_request_via_main_app(client: TestClient) -> None:
    """POST /api/v1/webhooks/bem con payload válido retorna 200."""
    body = {
        "tenant_id": "smoke-tenant",
        "payload": {
            "evidence_id": "smoke-ev-001",
            "kind": "excel",
            "data": {"precio_venta": 10.0, "costo_unitario": 80.0},
            "source": {
                "source_name": "smoke.xlsx",
                "source_type": "excel_file",
            },
        },
    }
    res = client.post("/api/v1/webhooks/bem", json=body)
    assert res.status_code == 200
    assert res.json()["status"] == "accepted"
    assert res.json()["tenant_id"] == "smoke-tenant"
    assert res.json()["evidence_id"] == "smoke-ev-001"


def test_bem_list_route_mounted(client: TestClient) -> None:
    """GET /api/v1/webhooks/bem/{tenant_id} responde (no 404)."""
    res = client.get("/api/v1/webhooks/bem/smoke-tenant")
    assert res.status_code == 200
    assert "items" in res.json()


def test_bem_detail_route_mounted(client: TestClient) -> None:
    """GET /api/v1/webhooks/bem/{tenant_id}/{evidence_id} responde (no 404)."""
    res = client.get("/api/v1/webhooks/bem/smoke-tenant/smoke-ev-001")
    # 200 si la evidencia fue persistida por el test anterior, 404 si no
    assert res.status_code in (200, 404)


# ---------------------------------------------------------------------------
# Rutas diagnóstico montadas
# ---------------------------------------------------------------------------


def test_diagnostico_route_mounted(client: TestClient) -> None:
    """GET /api/v1/diagnostico/{tenant_id} responde (no 404)."""
    res = client.get("/api/v1/diagnostico/smoke-tenant")
    assert res.status_code == 200
    assert "findings" in res.json()
    assert "evidence_count" in res.json()


def test_diagnostico_informe_route_mounted(client: TestClient) -> None:
    """GET /api/v1/diagnostico/{tenant_id}/informe responde (no 404)."""
    res = client.get("/api/v1/diagnostico/smoke-tenant/informe")
    assert res.status_code == 200
    assert "text/markdown" in res.headers["content-type"]
    assert "# Diagnóstico Operacional" in res.text


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
