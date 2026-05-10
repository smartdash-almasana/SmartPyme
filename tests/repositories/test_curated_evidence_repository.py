"""
Tests determinísticos para CuratedEvidenceRepositoryBackend.

Usa SQLite en memoria (tempfile) para aislamiento total.
Sin mocks. Sin side effects. Fail-closed.
"""
from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from app.contracts.bem_payloads import (
    BemConfidenceScore,
    BemSourceMetadata,
    CuratedEvidenceRecord,
    EvidenceKind,
)
from app.repositories.curated_evidence_repository import CuratedEvidenceRepositoryBackend


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def db_path(tmp_path: Path) -> Path:
    return tmp_path / "test_curated_evidence.db"


@pytest.fixture()
def repo(db_path: Path) -> CuratedEvidenceRepositoryBackend:
    return CuratedEvidenceRepositoryBackend(db_path=db_path)


def _make_record(
    tenant_id: str = "tenant-a",
    evidence_id: str = "ev-001",
    kind: EvidenceKind = EvidenceKind.EXCEL,
    payload: dict | None = None,
    source_name: str = "ventas_2024.xlsx",
    source_type: str = "excel",
    received_at: str = "2024-01-15T10:00:00+00:00",
    confidence_score: float | None = None,
    trace_id: str | None = None,
) -> CuratedEvidenceRecord:
    source = BemSourceMetadata(source_name=source_name, source_type=source_type)
    confidence = BemConfidenceScore(score=confidence_score) if confidence_score is not None else None
    return CuratedEvidenceRecord(
        tenant_id=tenant_id,
        evidence_id=evidence_id,
        kind=kind,
        payload=payload or {"rows": 100, "sheet": "Ventas"},
        source_metadata=source,
        received_at=received_at,
        confidence=confidence,
        trace_id=trace_id,
    )


# ---------------------------------------------------------------------------
# create válido
# ---------------------------------------------------------------------------


def test_create_valid(repo: CuratedEvidenceRepositoryBackend) -> None:
    record = _make_record()
    repo.create(record)  # no debe lanzar


# ---------------------------------------------------------------------------
# get válido
# ---------------------------------------------------------------------------


def test_get_by_evidence_id_returns_record(repo: CuratedEvidenceRepositoryBackend) -> None:
    record = _make_record(tenant_id="tenant-a", evidence_id="ev-001")
    repo.create(record)

    result = repo.get_by_evidence_id("tenant-a", "ev-001")

    assert result is not None
    assert result.tenant_id == "tenant-a"
    assert result.evidence_id == "ev-001"
    assert result.kind == EvidenceKind.EXCEL
    assert result.received_at == "2024-01-15T10:00:00+00:00"


# ---------------------------------------------------------------------------
# evidence inexistente
# ---------------------------------------------------------------------------


def test_get_by_evidence_id_returns_none_when_not_found(
    repo: CuratedEvidenceRepositoryBackend,
) -> None:
    result = repo.get_by_evidence_id("tenant-a", "ev-inexistente")
    assert result is None


# ---------------------------------------------------------------------------
# list_by_tenant
# ---------------------------------------------------------------------------


def test_list_by_tenant_returns_all_records(repo: CuratedEvidenceRepositoryBackend) -> None:
    repo.create(_make_record(evidence_id="ev-001", received_at="2024-01-15T10:00:00+00:00"))
    repo.create(_make_record(evidence_id="ev-002", received_at="2024-01-16T10:00:00+00:00"))

    results = repo.list_by_tenant("tenant-a")

    assert len(results) == 2
    ids = {r.evidence_id for r in results}
    assert ids == {"ev-001", "ev-002"}


def test_list_by_tenant_empty_returns_empty_list(repo: CuratedEvidenceRepositoryBackend) -> None:
    results = repo.list_by_tenant("tenant-sin-datos")
    assert results == []


# ---------------------------------------------------------------------------
# tenant isolation
# ---------------------------------------------------------------------------


def test_tenant_isolation_get(repo: CuratedEvidenceRepositoryBackend) -> None:
    repo.create(_make_record(tenant_id="tenant-a", evidence_id="ev-001"))
    repo.create(_make_record(tenant_id="tenant-b", evidence_id="ev-001"))

    result_a = repo.get_by_evidence_id("tenant-a", "ev-001")
    result_b = repo.get_by_evidence_id("tenant-b", "ev-001")

    assert result_a is not None
    assert result_a.tenant_id == "tenant-a"
    assert result_b is not None
    assert result_b.tenant_id == "tenant-b"


def test_tenant_isolation_list(repo: CuratedEvidenceRepositoryBackend) -> None:
    repo.create(_make_record(tenant_id="tenant-a", evidence_id="ev-001"))
    repo.create(_make_record(tenant_id="tenant-a", evidence_id="ev-002"))
    repo.create(_make_record(tenant_id="tenant-b", evidence_id="ev-003"))

    results_a = repo.list_by_tenant("tenant-a")
    results_b = repo.list_by_tenant("tenant-b")

    assert len(results_a) == 2
    assert all(r.tenant_id == "tenant-a" for r in results_a)

    assert len(results_b) == 1
    assert results_b[0].tenant_id == "tenant-b"
    assert results_b[0].evidence_id == "ev-003"


def test_tenant_b_cannot_see_tenant_a_evidence(repo: CuratedEvidenceRepositoryBackend) -> None:
    repo.create(_make_record(tenant_id="tenant-a", evidence_id="ev-secreto"))

    result = repo.get_by_evidence_id("tenant-b", "ev-secreto")
    assert result is None


# ---------------------------------------------------------------------------
# payload persistido
# ---------------------------------------------------------------------------


def test_payload_persisted_correctly(repo: CuratedEvidenceRepositoryBackend) -> None:
    payload = {"rows": 250, "sheet": "Compras", "currency": "ARS"}
    record = _make_record(payload=payload)
    repo.create(record)

    result = repo.get_by_evidence_id("tenant-a", "ev-001")

    assert result is not None
    assert result.payload == payload


# ---------------------------------------------------------------------------
# source persistido
# ---------------------------------------------------------------------------


def test_source_persisted_correctly(repo: CuratedEvidenceRepositoryBackend) -> None:
    record = _make_record(source_name="stock_enero.xlsx", source_type="excel")
    repo.create(record)

    result = repo.get_by_evidence_id("tenant-a", "ev-001")

    assert result is not None
    assert result.source_metadata.source_name == "stock_enero.xlsx"
    assert result.source_metadata.source_type == "excel"


# ---------------------------------------------------------------------------
# confidence persistido
# ---------------------------------------------------------------------------


def test_confidence_persisted_when_present(repo: CuratedEvidenceRepositoryBackend) -> None:
    record = _make_record(confidence_score=0.87)
    repo.create(record)

    result = repo.get_by_evidence_id("tenant-a", "ev-001")

    assert result is not None
    assert result.confidence is not None
    assert result.confidence.score == pytest.approx(0.87)


def test_confidence_none_when_not_provided(repo: CuratedEvidenceRepositoryBackend) -> None:
    record = _make_record(confidence_score=None)
    repo.create(record)

    result = repo.get_by_evidence_id("tenant-a", "ev-001")

    assert result is not None
    assert result.confidence is None


# ---------------------------------------------------------------------------
# tenant vacío fail-closed
# ---------------------------------------------------------------------------


def test_create_fails_on_empty_tenant_id(repo: CuratedEvidenceRepositoryBackend) -> None:
    # CuratedEvidenceRecord.__post_init__ ya valida tenant_id antes de llegar al repo.
    # El sistema es fail-closed: la validación ocurre en la construcción del contrato.
    with pytest.raises(ValueError, match="tenant_id"):
        _make_record(tenant_id="  ")


def test_get_fails_on_empty_tenant_id(repo: CuratedEvidenceRepositoryBackend) -> None:
    with pytest.raises(ValueError, match="tenant_id"):
        repo.get_by_evidence_id("", "ev-001")


def test_list_fails_on_empty_tenant_id(repo: CuratedEvidenceRepositoryBackend) -> None:
    with pytest.raises(ValueError, match="tenant_id"):
        repo.list_by_tenant("")


def test_get_fails_on_empty_evidence_id(repo: CuratedEvidenceRepositoryBackend) -> None:
    with pytest.raises(ValueError, match="evidence_id"):
        repo.get_by_evidence_id("tenant-a", "")


# ---------------------------------------------------------------------------
# trace_id persistido
# ---------------------------------------------------------------------------


def test_trace_id_persisted_when_present(repo: CuratedEvidenceRepositoryBackend) -> None:
    record = _make_record(trace_id="trace-xyz-123")
    repo.create(record)

    result = repo.get_by_evidence_id("tenant-a", "ev-001")

    assert result is not None
    assert result.trace_id == "trace-xyz-123"


def test_trace_id_none_when_not_provided(repo: CuratedEvidenceRepositoryBackend) -> None:
    record = _make_record(trace_id=None)
    repo.create(record)

    result = repo.get_by_evidence_id("tenant-a", "ev-001")

    assert result is not None
    assert result.trace_id is None


# ---------------------------------------------------------------------------
# duplicate primary key fail-closed
# ---------------------------------------------------------------------------


def test_create_fails_on_duplicate_primary_key(repo: CuratedEvidenceRepositoryBackend) -> None:
    record = _make_record(tenant_id="tenant-a", evidence_id="ev-dup")
    repo.create(record)

    import sqlite3

    with pytest.raises(sqlite3.IntegrityError):
        repo.create(record)
