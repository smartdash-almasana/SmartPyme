"""
Smoke test end-to-end: BEM webhook → diagnóstico operacional.

Flujo:
  1. POST /webhooks/bem  (precio_venta < costo_unitario)
  2. GET  /diagnostico/{tenant_id}
  3. Verificar evidence_count, VENTA_BAJO_COSTO, evidence_id

SQLite temporal. Routers inyectables. Sin DB real. Sin auth.
"""
from __future__ import annotations

from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.bem_webhook_router import _build_router
from app.api.diagnostic_router import _build_diagnostic_router
from app.repositories.curated_evidence_repository import CuratedEvidenceRepositoryBackend


# ---------------------------------------------------------------------------
# Fixture: app completa con DB compartida
# ---------------------------------------------------------------------------


@pytest.fixture()
def e2e_client(tmp_path: Path) -> TestClient:
    db_path = tmp_path / "e2e.db"
    repo = CuratedEvidenceRepositoryBackend(db_path=db_path)

    app = FastAPI()
    app.include_router(_build_router(repo))
    app.include_router(_build_diagnostic_router(repo))

    return TestClient(app)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _webhook_body(
    tenant_id: str = "tenant-e2e",
    evidence_id: str = "ev-e2e-001",
    precio_venta: float = 10.0,
    costo_unitario: float = 80.0,
) -> dict:
    return {
        "tenant_id": tenant_id,
        "payload": {
            "evidence_id": evidence_id,
            "kind": "excel",
            "data": {
                "precio_venta": precio_venta,
                "costo_unitario": costo_unitario,
            },
            "source": {
                "source_name": "ventas_enero.xlsx",
                "source_type": "excel_file",
            },
        },
    }


# ---------------------------------------------------------------------------
# Smoke E2E principal
# ---------------------------------------------------------------------------


def test_e2e_bem_to_diagnostic_venta_bajo_costo(e2e_client: TestClient) -> None:
    # 1. Ingestar evidencia con precio_venta < costo_unitario
    post_res = e2e_client.post("/webhooks/bem", json=_webhook_body())

    assert post_res.status_code == 200
    assert post_res.json()["status"] == "accepted"
    assert post_res.json()["evidence_id"] == "ev-e2e-001"
    assert post_res.json()["tenant_id"] == "tenant-e2e"

    # 2. Consultar diagnóstico
    get_res = e2e_client.get("/diagnostico/tenant-e2e")

    assert get_res.status_code == 200
    body = get_res.json()

    # 3. Verificar
    assert body["evidence_count"] == 1

    types = [f["finding_type"] for f in body["findings"]]
    assert "VENTA_BAJO_COSTO" in types

    finding = next(f for f in body["findings"] if f["finding_type"] == "VENTA_BAJO_COSTO")
    assert finding["evidence_id"] == "ev-e2e-001"
    assert finding["severity"] == "HIGH"


# ---------------------------------------------------------------------------
# E2E: múltiples evidencias, múltiples findings
# ---------------------------------------------------------------------------


def test_e2e_multiple_evidences_multiple_findings(e2e_client: TestClient) -> None:
    e2e_client.post("/webhooks/bem", json=_webhook_body(evidence_id="ev-001"))
    e2e_client.post(
        "/webhooks/bem",
        json={
            "tenant_id": "tenant-e2e",
            "payload": {
                "evidence_id": "ev-002",
                "kind": "excel",
                "data": {"stock_actual": -10},
                "source": {"source_name": "stock.xlsx", "source_type": "excel_file"},
            },
        },
    )

    res = e2e_client.get("/diagnostico/tenant-e2e")

    assert res.status_code == 200
    body = res.json()
    assert body["evidence_count"] == 2

    types = [f["finding_type"] for f in body["findings"]]
    assert "VENTA_BAJO_COSTO" in types
    assert "STOCK_NEGATIVO" in types


# ---------------------------------------------------------------------------
# E2E: tenant isolation — tenant-b no ve evidencia de tenant-a
# ---------------------------------------------------------------------------


def test_e2e_tenant_isolation(e2e_client: TestClient) -> None:
    e2e_client.post("/webhooks/bem", json=_webhook_body(tenant_id="tenant-a", evidence_id="ev-a"))

    res = e2e_client.get("/diagnostico/tenant-b")

    assert res.status_code == 200
    assert res.json()["evidence_count"] == 0
    assert res.json()["findings"] == []


# ---------------------------------------------------------------------------
# E2E: tenant sin evidencia → diagnóstico vacío
# ---------------------------------------------------------------------------


def test_e2e_empty_tenant_returns_empty_diagnostic(e2e_client: TestClient) -> None:
    res = e2e_client.get("/diagnostico/tenant-nuevo")

    assert res.status_code == 200
    assert res.json()["evidence_count"] == 0
    assert res.json()["findings"] == []
    assert res.json()["tenant_id"] == "tenant-nuevo"


# ---------------------------------------------------------------------------
# E2E: precio_venta >= costo_unitario → sin finding
# ---------------------------------------------------------------------------


def test_e2e_no_finding_when_precio_above_costo(e2e_client: TestClient) -> None:
    e2e_client.post(
        "/webhooks/bem",
        json=_webhook_body(
            evidence_id="ev-ok",
            precio_venta=200.0,
            costo_unitario=100.0,
        ),
    )

    res = e2e_client.get("/diagnostico/tenant-e2e")

    assert res.status_code == 200
    types = [f["finding_type"] for f in res.json()["findings"]]
    assert "VENTA_BAJO_COSTO" not in types
