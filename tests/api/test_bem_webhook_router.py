"""
Tests determinísticos para bem_webhook_router.

Cada test usa un SQLite temporal aislado via make_router(db_path=tmp_path/...).
Sin mocks. Sin side effects. Fail-closed.
"""
from __future__ import annotations

from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.bem_webhook_router import make_router
from app.repositories.curated_evidence_repository import CuratedEvidenceRepositoryBackend


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _client_with_db(db_path: Path) -> tuple[TestClient, CuratedEvidenceRepositoryBackend]:
    """Retorna (TestClient, repo) compartiendo el mismo archivo SQLite."""
    repo = CuratedEvidenceRepositoryBackend(db_path=db_path)
    from app.api.bem_webhook_router import _build_router

    app = FastAPI()
    app.include_router(_build_router(repo))
    return TestClient(app), repo


def _valid_body(
    tenant_id: str = "tenant-1",
    evidence_id: str = "ev-001",
    kind: str = "excel",
) -> dict:
    return {
        "tenant_id": tenant_id,
        "payload": {
            "evidence_id": evidence_id,
            "kind": kind,
            "data": {"sheet": "ventas", "rows": 10},
            "source": {
                "source_name": "upload_owner",
                "source_type": "excel_file",
            },
            "confidence": {"score": 0.9, "provider": "bem"},
            "trace_id": "trace-123",
        },
    }


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def db_path(tmp_path: Path) -> Path:
    return tmp_path / "test_webhook.db"


@pytest.fixture()
def client_and_repo(db_path: Path) -> tuple[TestClient, CuratedEvidenceRepositoryBackend]:
    return _client_with_db(db_path)


# ---------------------------------------------------------------------------
# Respuesta HTTP correcta
# ---------------------------------------------------------------------------


def test_bem_webhook_valid_request(
    client_and_repo: tuple[TestClient, CuratedEvidenceRepositoryBackend],
) -> None:
    client, _ = client_and_repo
    res = client.post("/webhooks/bem", json=_valid_body())

    assert res.status_code == 200
    assert res.json() == {
        "status": "accepted",
        "evidence_id": "ev-001",
        "tenant_id": "tenant-1",
    }


def test_bem_webhook_response_shape(
    client_and_repo: tuple[TestClient, CuratedEvidenceRepositoryBackend],
) -> None:
    client, _ = client_and_repo
    res = client.post("/webhooks/bem", json=_valid_body())
    body = res.json()

    assert res.status_code == 200
    assert body["status"] == "accepted"
    assert body["evidence_id"] == "ev-001"
    assert body["tenant_id"] == "tenant-1"


# ---------------------------------------------------------------------------
# Persistencia real
# ---------------------------------------------------------------------------


def test_webhook_persists_evidence(
    client_and_repo: tuple[TestClient, CuratedEvidenceRepositoryBackend],
) -> None:
    client, repo = client_and_repo
    res = client.post("/webhooks/bem", json=_valid_body())

    assert res.status_code == 200

    record = repo.get_by_evidence_id("tenant-1", "ev-001")
    assert record is not None
    assert record.tenant_id == "tenant-1"
    assert record.evidence_id == "ev-001"


def test_webhook_persists_payload_data(
    client_and_repo: tuple[TestClient, CuratedEvidenceRepositoryBackend],
) -> None:
    client, repo = client_and_repo
    client.post("/webhooks/bem", json=_valid_body())

    record = repo.get_by_evidence_id("tenant-1", "ev-001")
    assert record is not None
    assert record.payload == {"sheet": "ventas", "rows": 10}


def test_webhook_persists_source_metadata(
    client_and_repo: tuple[TestClient, CuratedEvidenceRepositoryBackend],
) -> None:
    client, repo = client_and_repo
    client.post("/webhooks/bem", json=_valid_body())

    record = repo.get_by_evidence_id("tenant-1", "ev-001")
    assert record is not None
    assert record.source_metadata.source_name == "upload_owner"
    assert record.source_metadata.source_type == "excel_file"


def test_webhook_persists_confidence(
    client_and_repo: tuple[TestClient, CuratedEvidenceRepositoryBackend],
) -> None:
    client, repo = client_and_repo
    client.post("/webhooks/bem", json=_valid_body())

    record = repo.get_by_evidence_id("tenant-1", "ev-001")
    assert record is not None
    assert record.confidence is not None
    assert record.confidence.score == pytest.approx(0.9)
    assert record.confidence.provider == "bem"


# ---------------------------------------------------------------------------
# Retrieval posterior
# ---------------------------------------------------------------------------


def test_webhook_evidence_retrievable_after_post(
    client_and_repo: tuple[TestClient, CuratedEvidenceRepositoryBackend],
) -> None:
    client, repo = client_and_repo

    client.post("/webhooks/bem", json=_valid_body(evidence_id="ev-A"))
    client.post("/webhooks/bem", json=_valid_body(evidence_id="ev-B"))

    results = repo.list_by_tenant("tenant-1")
    ids = {r.evidence_id for r in results}
    assert ids == {"ev-A", "ev-B"}


# ---------------------------------------------------------------------------
# Tenant isolation
# ---------------------------------------------------------------------------


def test_webhook_tenant_isolation(
    client_and_repo: tuple[TestClient, CuratedEvidenceRepositoryBackend],
) -> None:
    client, repo = client_and_repo

    client.post("/webhooks/bem", json=_valid_body(tenant_id="tenant-a", evidence_id="ev-001"))
    client.post("/webhooks/bem", json=_valid_body(tenant_id="tenant-b", evidence_id="ev-001"))

    records_a = repo.list_by_tenant("tenant-a")
    records_b = repo.list_by_tenant("tenant-b")

    assert len(records_a) == 1
    assert records_a[0].tenant_id == "tenant-a"

    assert len(records_b) == 1
    assert records_b[0].tenant_id == "tenant-b"


def test_webhook_tenant_b_cannot_see_tenant_a(
    client_and_repo: tuple[TestClient, CuratedEvidenceRepositoryBackend],
) -> None:
    client, repo = client_and_repo

    client.post("/webhooks/bem", json=_valid_body(tenant_id="tenant-a", evidence_id="ev-secreto"))

    result = repo.get_by_evidence_id("tenant-b", "ev-secreto")
    assert result is None


# ---------------------------------------------------------------------------
# Payload inválido
# ---------------------------------------------------------------------------


def test_bem_webhook_rejects_invalid_payload(
    client_and_repo: tuple[TestClient, CuratedEvidenceRepositoryBackend],
) -> None:
    client, _ = client_and_repo
    body = {"tenant_id": "tenant-1", "payload": "invalid"}

    res = client.post("/webhooks/bem", json=body)

    assert res.status_code == 400
    assert "payload" in res.json()["detail"]


def test_bem_webhook_rejects_empty_payload_dict(
    client_and_repo: tuple[TestClient, CuratedEvidenceRepositoryBackend],
) -> None:
    client, _ = client_and_repo
    body = {"tenant_id": "tenant-1", "payload": {}}

    res = client.post("/webhooks/bem", json=body)

    assert res.status_code == 400
    assert "payload" in res.json()["detail"]


# ---------------------------------------------------------------------------
# kind inválido
# ---------------------------------------------------------------------------


def test_bem_webhook_rejects_invalid_kind(
    client_and_repo: tuple[TestClient, CuratedEvidenceRepositoryBackend],
) -> None:
    client, _ = client_and_repo
    body = _valid_body()
    body["payload"]["kind"] = "invalid-kind"

    res = client.post("/webhooks/bem", json=body)

    assert res.status_code == 400
    assert "kind inválido" in res.json()["detail"]


# ---------------------------------------------------------------------------
# evidence_id faltante
# ---------------------------------------------------------------------------


def test_bem_webhook_rejects_missing_evidence_id(
    client_and_repo: tuple[TestClient, CuratedEvidenceRepositoryBackend],
) -> None:
    client, _ = client_and_repo
    body = _valid_body()
    del body["payload"]["evidence_id"]

    res = client.post("/webhooks/bem", json=body)

    assert res.status_code == 400
    assert "evidence_id" in res.json()["detail"]


# ---------------------------------------------------------------------------
# tenant_id faltante
# ---------------------------------------------------------------------------


def test_bem_webhook_rejects_missing_tenant(
    client_and_repo: tuple[TestClient, CuratedEvidenceRepositoryBackend],
) -> None:
    client, _ = client_and_repo
    body = _valid_body()
    del body["tenant_id"]

    res = client.post("/webhooks/bem", json=body)

    assert res.status_code == 400
    assert "tenant_id" in res.json()["detail"]


# ---------------------------------------------------------------------------
# body vacío
# ---------------------------------------------------------------------------


def test_bem_webhook_fail_closed_on_empty_body(
    client_and_repo: tuple[TestClient, CuratedEvidenceRepositoryBackend],
) -> None:
    client, _ = client_and_repo

    res = client.post("/webhooks/bem", json={})

    assert res.status_code == 400


# ---------------------------------------------------------------------------
# make_router con sqlite temporal
# ---------------------------------------------------------------------------


def test_make_router_uses_provided_db_path(tmp_path: Path) -> None:
    db = tmp_path / "custom.db"
    app = FastAPI()
    app.include_router(make_router(db_path=db))
    client = TestClient(app)

    res = client.post("/webhooks/bem", json=_valid_body())
    assert res.status_code == 200
    assert db.exists()

    repo = CuratedEvidenceRepositoryBackend(db_path=db)
    record = repo.get_by_evidence_id("tenant-1", "ev-001")
    assert record is not None
    assert record.evidence_id == "ev-001"

# ---------------------------------------------------------------------------
# GET /webhooks/bem/{tenant_id}/{evidence_id} — retrieval válido
# ---------------------------------------------------------------------------


def test_get_evidence_returns_200_after_post(
    client_and_repo: tuple[TestClient, CuratedEvidenceRepositoryBackend],
) -> None:
    client, _ = client_and_repo
    client.post("/webhooks/bem", json=_valid_body())

    res = client.get("/webhooks/bem/tenant-1/ev-001")

    assert res.status_code == 200
    body = res.json()
    assert body["tenant_id"] == "tenant-1"
    assert body["evidence_id"] == "ev-001"
    assert body["kind"] == "excel"


def test_get_evidence_response_shape(
    client_and_repo: tuple[TestClient, CuratedEvidenceRepositoryBackend],
) -> None:
    client, _ = client_and_repo
    client.post("/webhooks/bem", json=_valid_body())

    res = client.get("/webhooks/bem/tenant-1/ev-001")
    body = res.json()

    assert res.status_code == 200
    assert set(body.keys()) == {
        "tenant_id",
        "evidence_id",
        "kind",
        "payload",
        "trace_id",
        "received_at",
    }


# ---------------------------------------------------------------------------
# GET — payload correcto
# ---------------------------------------------------------------------------


def test_get_evidence_payload_correct(
    client_and_repo: tuple[TestClient, CuratedEvidenceRepositoryBackend],
) -> None:
    client, _ = client_and_repo
    client.post("/webhooks/bem", json=_valid_body())

    res = client.get("/webhooks/bem/tenant-1/ev-001")

    assert res.status_code == 200
    assert res.json()["payload"] == {"sheet": "ventas", "rows": 10}


# ---------------------------------------------------------------------------
# GET — trace_id correcto
# ---------------------------------------------------------------------------


def test_get_evidence_trace_id_correct(
    client_and_repo: tuple[TestClient, CuratedEvidenceRepositoryBackend],
) -> None:
    client, _ = client_and_repo
    client.post("/webhooks/bem", json=_valid_body())

    res = client.get("/webhooks/bem/tenant-1/ev-001")

    assert res.status_code == 200
    assert res.json()["trace_id"] == "trace-123"


def test_get_evidence_trace_id_none_when_absent(
    client_and_repo: tuple[TestClient, CuratedEvidenceRepositoryBackend],
) -> None:
    client, _ = client_and_repo
    body = _valid_body()
    del body["payload"]["trace_id"]
    client.post("/webhooks/bem", json=body)

    res = client.get("/webhooks/bem/tenant-1/ev-001")

    assert res.status_code == 200
    assert res.json()["trace_id"] is None


# ---------------------------------------------------------------------------
# GET — 404 inexistente
# ---------------------------------------------------------------------------


def test_get_evidence_returns_404_when_not_found(
    client_and_repo: tuple[TestClient, CuratedEvidenceRepositoryBackend],
) -> None:
    client, _ = client_and_repo

    res = client.get("/webhooks/bem/tenant-1/ev-inexistente")

    assert res.status_code == 404
    assert "no encontrada" in res.json()["detail"]


def test_get_evidence_404_for_unknown_tenant(
    client_and_repo: tuple[TestClient, CuratedEvidenceRepositoryBackend],
) -> None:
    client, _ = client_and_repo
    client.post("/webhooks/bem", json=_valid_body(tenant_id="tenant-a"))

    res = client.get("/webhooks/bem/tenant-desconocido/ev-001")

    assert res.status_code == 404


# ---------------------------------------------------------------------------
# GET — tenant isolation
# ---------------------------------------------------------------------------


def test_get_evidence_tenant_isolation(
    client_and_repo: tuple[TestClient, CuratedEvidenceRepositoryBackend],
) -> None:
    client, _ = client_and_repo

    client.post("/webhooks/bem", json=_valid_body(tenant_id="tenant-a", evidence_id="ev-001"))
    client.post("/webhooks/bem", json=_valid_body(tenant_id="tenant-b", evidence_id="ev-001"))

    res_a = client.get("/webhooks/bem/tenant-a/ev-001")
    res_b = client.get("/webhooks/bem/tenant-b/ev-001")

    assert res_a.status_code == 200
    assert res_a.json()["tenant_id"] == "tenant-a"

    assert res_b.status_code == 200
    assert res_b.json()["tenant_id"] == "tenant-b"


def test_get_evidence_tenant_b_cannot_access_tenant_a_via_get(
    client_and_repo: tuple[TestClient, CuratedEvidenceRepositoryBackend],
) -> None:
    client, _ = client_and_repo

    client.post("/webhooks/bem", json=_valid_body(tenant_id="tenant-a", evidence_id="ev-secreto"))

    res = client.get("/webhooks/bem/tenant-b/ev-secreto")

    assert res.status_code == 404


# ---------------------------------------------------------------------------
# GET /webhooks/bem/{tenant_id} — lista por tenant
# ---------------------------------------------------------------------------


def _valid_body_with_ts(
    evidence_id: str,
    received_at_override: str | None = None,
    tenant_id: str = "tenant-1",
) -> dict:
    """
    Construye un body válido. received_at_override no se puede inyectar
    directamente en el webhook (lo genera el adapter), así que para tests
    de ordering insertamos directamente en el repo.
    """
    return _valid_body(tenant_id=tenant_id, evidence_id=evidence_id)


def test_list_evidence_returns_200_with_items(
    client_and_repo: tuple[TestClient, CuratedEvidenceRepositoryBackend],
) -> None:
    client, _ = client_and_repo
    client.post("/webhooks/bem", json=_valid_body(evidence_id="ev-001"))
    client.post("/webhooks/bem", json=_valid_body(evidence_id="ev-002"))

    res = client.get("/webhooks/bem/tenant-1")

    assert res.status_code == 200
    body = res.json()
    assert body["tenant_id"] == "tenant-1"
    assert len(body["items"]) == 2


def test_list_evidence_response_shape(
    client_and_repo: tuple[TestClient, CuratedEvidenceRepositoryBackend],
) -> None:
    client, _ = client_and_repo
    client.post("/webhooks/bem", json=_valid_body(evidence_id="ev-001"))

    res = client.get("/webhooks/bem/tenant-1")
    body = res.json()

    assert res.status_code == 200
    assert "tenant_id" in body
    assert "items" in body
    item = body["items"][0]
    assert set(item.keys()) == {"evidence_id", "kind", "trace_id", "received_at"}


def test_list_evidence_items_contain_correct_fields(
    client_and_repo: tuple[TestClient, CuratedEvidenceRepositoryBackend],
) -> None:
    client, _ = client_and_repo
    client.post("/webhooks/bem", json=_valid_body(evidence_id="ev-001", kind="pdf"))

    res = client.get("/webhooks/bem/tenant-1")
    item = res.json()["items"][0]

    assert item["evidence_id"] == "ev-001"
    assert item["kind"] == "pdf"
    assert item["trace_id"] == "trace-123"
    assert item["received_at"] is not None


# ---------------------------------------------------------------------------
# tenant vacío → lista vacía (no 404)
# ---------------------------------------------------------------------------


def test_list_evidence_empty_tenant_returns_empty_items(
    client_and_repo: tuple[TestClient, CuratedEvidenceRepositoryBackend],
) -> None:
    client, _ = client_and_repo

    res = client.get("/webhooks/bem/tenant-sin-datos")

    assert res.status_code == 200
    body = res.json()
    assert body["tenant_id"] == "tenant-sin-datos"
    assert body["items"] == []


# ---------------------------------------------------------------------------
# tenant inexistente → lista vacía (no 404)
# ---------------------------------------------------------------------------


def test_list_evidence_unknown_tenant_returns_empty_items(
    client_and_repo: tuple[TestClient, CuratedEvidenceRepositoryBackend],
) -> None:
    client, _ = client_and_repo
    client.post("/webhooks/bem", json=_valid_body(tenant_id="tenant-a", evidence_id="ev-001"))

    res = client.get("/webhooks/bem/tenant-inexistente")

    assert res.status_code == 200
    assert res.json()["items"] == []


# ---------------------------------------------------------------------------
# isolation multi-tenant
# ---------------------------------------------------------------------------


def test_list_evidence_isolation_multi_tenant(
    client_and_repo: tuple[TestClient, CuratedEvidenceRepositoryBackend],
) -> None:
    client, _ = client_and_repo

    client.post("/webhooks/bem", json=_valid_body(tenant_id="tenant-a", evidence_id="ev-001"))
    client.post("/webhooks/bem", json=_valid_body(tenant_id="tenant-a", evidence_id="ev-002"))
    client.post("/webhooks/bem", json=_valid_body(tenant_id="tenant-b", evidence_id="ev-003"))

    res_a = client.get("/webhooks/bem/tenant-a")
    res_b = client.get("/webhooks/bem/tenant-b")

    assert res_a.status_code == 200
    assert res_b.status_code == 200

    ids_a = {i["evidence_id"] for i in res_a.json()["items"]}
    ids_b = {i["evidence_id"] for i in res_b.json()["items"]}

    assert ids_a == {"ev-001", "ev-002"}
    assert ids_b == {"ev-003"}
    assert ids_a.isdisjoint(ids_b)


def test_list_evidence_tenant_b_sees_zero_from_tenant_a(
    client_and_repo: tuple[TestClient, CuratedEvidenceRepositoryBackend],
) -> None:
    client, _ = client_and_repo

    client.post("/webhooks/bem", json=_valid_body(tenant_id="tenant-a", evidence_id="ev-001"))
    client.post("/webhooks/bem", json=_valid_body(tenant_id="tenant-a", evidence_id="ev-002"))

    res = client.get("/webhooks/bem/tenant-b")

    assert res.status_code == 200
    assert res.json()["items"] == []


# ---------------------------------------------------------------------------
# ordering correcto (received_at asc)
# ---------------------------------------------------------------------------


def test_list_evidence_ordering_asc_by_received_at(
    client_and_repo: tuple[TestClient, CuratedEvidenceRepositoryBackend],
) -> None:
    """
    Inserta directamente en el repo con received_at controlados para
    verificar que list_by_tenant retorna en orden ascendente.
    """
    from app.contracts.bem_payloads import (
        BemConfidenceScore,
        BemSourceMetadata,
        CuratedEvidenceRecord,
        EvidenceKind,
    )

    _, repo = client_and_repo

    source = BemSourceMetadata(source_name="f.xlsx", source_type="excel")

    repo.create(
        CuratedEvidenceRecord(
            tenant_id="tenant-ord",
            evidence_id="ev-C",
            kind=EvidenceKind.EXCEL,
            payload={"x": 1},
            source_metadata=source,
            received_at="2024-03-01T10:00:00+00:00",
        )
    )
    repo.create(
        CuratedEvidenceRecord(
            tenant_id="tenant-ord",
            evidence_id="ev-A",
            kind=EvidenceKind.EXCEL,
            payload={"x": 1},
            source_metadata=source,
            received_at="2024-01-01T10:00:00+00:00",
        )
    )
    repo.create(
        CuratedEvidenceRecord(
            tenant_id="tenant-ord",
            evidence_id="ev-B",
            kind=EvidenceKind.EXCEL,
            payload={"x": 1},
            source_metadata=source,
            received_at="2024-02-01T10:00:00+00:00",
        )
    )

    # Usar el mismo repo en el cliente
    from app.api.bem_webhook_router import _build_router
    from fastapi import FastAPI
    from fastapi.testclient import TestClient as TC

    app = FastAPI()
    app.include_router(_build_router(repo))
    c = TC(app)

    res = c.get("/webhooks/bem/tenant-ord")
    assert res.status_code == 200
    ids = [i["evidence_id"] for i in res.json()["items"]]
    assert ids == ["ev-A", "ev-B", "ev-C"]


# ---------------------------------------------------------------------------
# Case-insensitive kind parsing via webhook
# ---------------------------------------------------------------------------


def test_bem_webhook_accepts_uppercase_kind(
    client_and_repo: tuple[TestClient, CuratedEvidenceRepositoryBackend],
) -> None:
    client, repo = client_and_repo
    body = _valid_body()
    body["payload"]["kind"] = "EXCEL"

    res = client.post("/webhooks/bem", json=body)

    assert res.status_code == 200
    record = repo.get_by_evidence_id("tenant-1", "ev-001")
    assert record is not None
    assert record.kind.value == "excel"


def test_bem_webhook_accepts_mixed_case_kind(
    client_and_repo: tuple[TestClient, CuratedEvidenceRepositoryBackend],
) -> None:
    client, _ = client_and_repo
    body = _valid_body()
    body["payload"]["kind"] = "Excel"

    res = client.post("/webhooks/bem", json=body)

    assert res.status_code == 200
