"""
Tests determinísticos para diagnostic_router.

Cada test usa un SQLite temporal aislado.
Sin mocks. Sin side effects. Fail-closed.
"""
from __future__ import annotations

from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.diagnostic_router import _build_diagnostic_router, make_diagnostic_router
from app.contracts.bem_payloads import (
    BemSourceMetadata,
    CuratedEvidenceRecord,
    EvidenceKind,
)
from app.repositories.curated_evidence_repository import CuratedEvidenceRepositoryBackend


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_SOURCE = BemSourceMetadata(source_name="archivo.xlsx", source_type="excel")


def _client_with_repo(
    repo: CuratedEvidenceRepositoryBackend,
) -> TestClient:
    app = FastAPI()
    app.include_router(_build_diagnostic_router(repo))
    return TestClient(app)


def _insert(
    repo: CuratedEvidenceRepositoryBackend,
    evidence_id: str,
    payload: dict,
    tenant_id: str = "tenant-1",
) -> None:
    repo.create(
        CuratedEvidenceRecord(
            tenant_id=tenant_id,
            evidence_id=evidence_id,
            kind=EvidenceKind.EXCEL,
            payload=payload,
            source_metadata=_SOURCE,
            received_at="2024-01-15T10:00:00+00:00",
        )
    )


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def repo(tmp_path: Path) -> CuratedEvidenceRepositoryBackend:
    return CuratedEvidenceRepositoryBackend(db_path=tmp_path / "diag.db")


@pytest.fixture()
def client(repo: CuratedEvidenceRepositoryBackend) -> TestClient:
    return _client_with_repo(repo)


# ---------------------------------------------------------------------------
# Response shape
# ---------------------------------------------------------------------------


def test_diagnostico_response_shape(
    repo: CuratedEvidenceRepositoryBackend,
    client: TestClient,
) -> None:
    _insert(repo, "ev-001", {"x": 1})

    res = client.get("/diagnostico/tenant-1")

    assert res.status_code == 200
    body = res.json()
    assert set(body.keys()) == {"tenant_id", "findings", "evidence_count"}
    assert body["tenant_id"] == "tenant-1"
    assert isinstance(body["findings"], list)
    assert isinstance(body["evidence_count"], int)


# ---------------------------------------------------------------------------
# Tenant con findings
# ---------------------------------------------------------------------------


def test_diagnostico_returns_findings(
    repo: CuratedEvidenceRepositoryBackend,
    client: TestClient,
) -> None:
    _insert(repo, "ev-001", {"precio_venta": 10.0, "costo_unitario": 50.0})

    res = client.get("/diagnostico/tenant-1")

    assert res.status_code == 200
    body = res.json()
    assert body["evidence_count"] == 1
    types = [f["finding_type"] for f in body["findings"]]
    assert "VENTA_BAJO_COSTO" in types


def test_diagnostico_finding_shape(
    repo: CuratedEvidenceRepositoryBackend,
    client: TestClient,
) -> None:
    _insert(repo, "ev-001", {"precio_venta": 5.0, "costo_unitario": 20.0})

    res = client.get("/diagnostico/tenant-1")
    finding = res.json()["findings"][0]

    assert set(finding.keys()) == {"finding_type", "severity", "message", "evidence_id"}
    assert finding["severity"] == "HIGH"
    assert finding["evidence_id"] == "ev-001"


def test_diagnostico_stock_negativo_finding(
    repo: CuratedEvidenceRepositoryBackend,
    client: TestClient,
) -> None:
    _insert(repo, "ev-001", {"stock_actual": -5})

    res = client.get("/diagnostico/tenant-1")
    types = [f["finding_type"] for f in res.json()["findings"]]

    assert "STOCK_NEGATIVO" in types


def test_diagnostico_movimiento_inconsistente_finding(
    repo: CuratedEvidenceRepositoryBackend,
    client: TestClient,
) -> None:
    _insert(repo, "ev-001", {"cantidad": 0, "monto_total": 300.0})

    res = client.get("/diagnostico/tenant-1")
    types = [f["finding_type"] for f in res.json()["findings"]]

    assert "MOVIMIENTO_INCONSISTENTE" in types


# ---------------------------------------------------------------------------
# Tenant sin evidencia
# ---------------------------------------------------------------------------


def test_diagnostico_empty_tenant_returns_no_findings(
    client: TestClient,
) -> None:
    res = client.get("/diagnostico/tenant-sin-datos")

    assert res.status_code == 200
    body = res.json()
    assert body["findings"] == []
    assert body["evidence_count"] == 0
    assert body["tenant_id"] == "tenant-sin-datos"


# ---------------------------------------------------------------------------
# Tenant isolation
# ---------------------------------------------------------------------------


def test_diagnostico_tenant_isolation(
    repo: CuratedEvidenceRepositoryBackend,
    client: TestClient,
) -> None:
    _insert(
        repo, "ev-001",
        {"precio_venta": 1.0, "costo_unitario": 100.0},
        tenant_id="tenant-a",
    )
    _insert(
        repo, "ev-002",
        {"stock_actual": 50},
        tenant_id="tenant-b",
    )

    res_a = client.get("/diagnostico/tenant-a")
    res_b = client.get("/diagnostico/tenant-b")

    assert res_a.status_code == 200
    assert res_b.status_code == 200

    types_a = [f["finding_type"] for f in res_a.json()["findings"]]
    types_b = [f["finding_type"] for f in res_b.json()["findings"]]

    assert "VENTA_BAJO_COSTO" in types_a
    assert "VENTA_BAJO_COSTO" not in types_b

    assert res_a.json()["evidence_count"] == 1
    assert res_b.json()["evidence_count"] == 1


def test_diagnostico_tenant_b_sees_zero_from_tenant_a(
    repo: CuratedEvidenceRepositoryBackend,
    client: TestClient,
) -> None:
    _insert(repo, "ev-001", {"precio_venta": 1.0, "costo_unitario": 100.0}, tenant_id="tenant-a")
    _insert(repo, "ev-002", {"precio_venta": 1.0, "costo_unitario": 100.0}, tenant_id="tenant-a")

    res = client.get("/diagnostico/tenant-b")

    assert res.status_code == 200
    assert res.json()["evidence_count"] == 0
    assert res.json()["findings"] == []


# ---------------------------------------------------------------------------
# Tenant vacío / inválido
# ---------------------------------------------------------------------------


def test_diagnostico_rejects_empty_tenant_in_path(
    client: TestClient,
) -> None:
    # FastAPI no enruta paths vacíos — el endpoint no existe para ""
    # Verificamos que un tenant con solo espacios en la query no pase.
    # Para el path vacío, FastAPI retorna 404 (no hay ruta).
    res = client.get("/diagnostico/   ")
    # Espacios en path son codificados; el servicio los rechaza con 400.
    assert res.status_code in (400, 404, 422)


def test_diagnostico_rejects_blank_tenant_via_service(
    repo: CuratedEvidenceRepositoryBackend,
) -> None:
    """El servicio falla directamente con ValueError para tenant_id en blanco."""
    from app.services.basic_operational_diagnostic_service import (
        BasicOperationalDiagnosticService,
    )

    service = BasicOperationalDiagnosticService(repository=repo)
    with pytest.raises(ValueError, match="tenant_id"):
        service.build_report("   ")


# ---------------------------------------------------------------------------
# make_diagnostic_router con sqlite temporal
# ---------------------------------------------------------------------------


def test_make_diagnostic_router_uses_provided_db_path(tmp_path: Path) -> None:
    db = tmp_path / "custom_diag.db"

    # Insertar evidencia directamente en el repo con ese path
    repo = CuratedEvidenceRepositoryBackend(db_path=db)
    _insert(repo, "ev-001", {"precio_venta": 1.0, "costo_unitario": 50.0})

    app = FastAPI()
    app.include_router(make_diagnostic_router(db_path=db))
    client = TestClient(app)

    res = client.get("/diagnostico/tenant-1")

    assert res.status_code == 200
    assert db.exists()
    types = [f["finding_type"] for f in res.json()["findings"]]
    assert "VENTA_BAJO_COSTO" in types


def test_make_diagnostic_router_empty_tenant_returns_empty(tmp_path: Path) -> None:
    db = tmp_path / "empty_diag.db"
    app = FastAPI()
    app.include_router(make_diagnostic_router(db_path=db))
    client = TestClient(app)

    res = client.get("/diagnostico/tenant-inexistente")

    assert res.status_code == 200
    assert res.json()["findings"] == []
    assert res.json()["evidence_count"] == 0


# ---------------------------------------------------------------------------
# GET /diagnostico/{tenant_id}/informe — informe Markdown
# ---------------------------------------------------------------------------


def test_informe_returns_200(
    repo: CuratedEvidenceRepositoryBackend,
    client: TestClient,
) -> None:
    _insert(repo, "ev-001", {"precio_venta": 10.0, "costo_unitario": 50.0})

    res = client.get("/diagnostico/tenant-1/informe")

    assert res.status_code == 200


def test_informe_media_type_is_text_markdown(
    repo: CuratedEvidenceRepositoryBackend,
    client: TestClient,
) -> None:
    _insert(repo, "ev-001", {"precio_venta": 10.0, "costo_unitario": 50.0})

    res = client.get("/diagnostico/tenant-1/informe")

    assert "text/markdown" in res.headers["content-type"]


def test_informe_contains_markdown_header(
    repo: CuratedEvidenceRepositoryBackend,
    client: TestClient,
) -> None:
    _insert(repo, "ev-001", {"x": 1})

    res = client.get("/diagnostico/tenant-1/informe")

    assert "# Diagnóstico Operacional" in res.text


def test_informe_contains_tenant_id(
    repo: CuratedEvidenceRepositoryBackend,
    client: TestClient,
) -> None:
    _insert(repo, "ev-001", {"x": 1})

    res = client.get("/diagnostico/tenant-1/informe")

    assert "tenant-1" in res.text


def test_informe_tenant_con_venta_bajo_costo(
    repo: CuratedEvidenceRepositoryBackend,
    client: TestClient,
) -> None:
    _insert(repo, "ev-001", {"precio_venta": 5.0, "costo_unitario": 100.0})

    res = client.get("/diagnostico/tenant-1/informe")

    assert res.status_code == 200
    assert "VENTA_BAJO_COSTO" in res.text
    assert "HIGH" in res.text
    assert "ev-001" in res.text


def test_informe_tenant_sin_findings(
    client: TestClient,
) -> None:
    res = client.get("/diagnostico/tenant-sin-datos/informe")

    assert res.status_code == 200
    assert "No se detectaron hallazgos operacionales." in res.text


def test_informe_tenant_isolation(
    repo: CuratedEvidenceRepositoryBackend,
    client: TestClient,
) -> None:
    _insert(
        repo, "ev-a",
        {"precio_venta": 1.0, "costo_unitario": 100.0},
        tenant_id="tenant-a",
    )

    res_a = client.get("/diagnostico/tenant-a/informe")
    res_b = client.get("/diagnostico/tenant-b/informe")

    assert "VENTA_BAJO_COSTO" in res_a.text
    assert "VENTA_BAJO_COSTO" not in res_b.text
    assert "No se detectaron hallazgos operacionales." in res_b.text


def test_informe_does_not_interfere_with_json_endpoint(
    repo: CuratedEvidenceRepositoryBackend,
    client: TestClient,
) -> None:
    """El endpoint /informe no debe romper GET /{tenant_id} JSON."""
    _insert(repo, "ev-001", {"precio_venta": 5.0, "costo_unitario": 100.0})

    json_res = client.get("/diagnostico/tenant-1")
    md_res = client.get("/diagnostico/tenant-1/informe")

    assert json_res.status_code == 200
    assert md_res.status_code == 200
    assert json_res.json()["tenant_id"] == "tenant-1"
    assert "# Diagnóstico Operacional" in md_res.text


# ---------------------------------------------------------------------------
# GET /diagnostico/{tenant_id}/informe — Content-Disposition header
# ---------------------------------------------------------------------------


def test_informe_content_disposition_header_present(
    repo: CuratedEvidenceRepositoryBackend,
    client: TestClient,
) -> None:
    _insert(repo, "ev-001", {"x": 1})

    res = client.get("/diagnostico/tenant-1/informe")

    assert "content-disposition" in res.headers


def test_informe_content_disposition_is_attachment(
    repo: CuratedEvidenceRepositoryBackend,
    client: TestClient,
) -> None:
    _insert(repo, "ev-001", {"x": 1})

    res = client.get("/diagnostico/tenant-1/informe")

    assert "attachment" in res.headers["content-disposition"]


def test_informe_content_disposition_filename_contains_tenant_id(
    repo: CuratedEvidenceRepositoryBackend,
    client: TestClient,
) -> None:
    _insert(repo, "ev-001", {"x": 1})

    res = client.get("/diagnostico/tenant-abc/informe")

    assert "tenant-abc" in res.headers["content-disposition"]
    assert "diagnostico-tenant-abc.md" in res.headers["content-disposition"]


def test_informe_body_markdown_unchanged_with_header(
    repo: CuratedEvidenceRepositoryBackend,
    client: TestClient,
) -> None:
    _insert(repo, "ev-001", {"precio_venta": 5.0, "costo_unitario": 100.0})

    res = client.get("/diagnostico/tenant-1/informe")

    assert res.status_code == 200
    assert "# Diagnóstico Operacional" in res.text
    assert "VENTA_BAJO_COSTO" in res.text
    assert "text/markdown" in res.headers["content-type"]


def test_informe_content_disposition_tenant_sin_findings(
    client: TestClient,
) -> None:
    res = client.get("/diagnostico/tenant-vacio/informe")

    assert res.status_code == 200
    assert "attachment" in res.headers["content-disposition"]
    assert "diagnostico-tenant-vacio.md" in res.headers["content-disposition"]
    assert "No se detectaron hallazgos operacionales." in res.text
