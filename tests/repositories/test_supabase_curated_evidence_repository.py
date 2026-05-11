from __future__ import annotations

import pytest

from app.contracts.bem_payloads import BemSourceMetadata, CuratedEvidenceRecord, EvidenceKind
from app.repositories.supabase_curated_evidence_repository import SupabaseCuratedEvidenceRepository


class _FakeResult:
    def __init__(self, data: list[dict]) -> None:
        self.data = data


class _FakeQueryBuilder:
    def __init__(self, store: list[dict]) -> None:
        self._store = store
        self._filters: list[tuple[str, object]] = []
        self._mode = "select"
        self._upsert_row: dict | None = None

    def select(self, cols: str = "*") -> "_FakeQueryBuilder":
        self._mode = "select"
        return self

    def eq(self, col: str, val: object) -> "_FakeQueryBuilder":
        self._filters.append((col, val))
        return self

    def upsert(self, row: dict, on_conflict: str | None = None) -> "_FakeQueryBuilder":
        self._mode = "upsert"
        self._upsert_row = dict(row)
        return self

    def execute(self) -> _FakeResult:
        if self._mode == "upsert":
            assert self._upsert_row is not None
            tenant = self._upsert_row.get("tenant_id")
            evidence = self._upsert_row.get("evidence_id")
            replaced = False
            for idx, existing in enumerate(self._store):
                if existing.get("tenant_id") == tenant and existing.get("evidence_id") == evidence:
                    self._store[idx] = dict(self._upsert_row)
                    replaced = True
                    break
            if not replaced:
                self._store.append(dict(self._upsert_row))
            return _FakeResult([])

        rows = list(self._store)
        for col, val in self._filters:
            rows = [r for r in rows if r.get(col) == val]
        return _FakeResult(rows)


class FakeSupabaseClient:
    def __init__(self) -> None:
        self._tables: dict[str, list[dict]] = {}

    def table(self, name: str) -> _FakeQueryBuilder:
        if name not in self._tables:
            self._tables[name] = []
        return _FakeQueryBuilder(self._tables[name])

    def get_rows(self, name: str) -> list[dict]:
        return list(self._tables.get(name, []))


def _make_record(
    *,
    tenant_id: str = "tenant-a",
    evidence_id: str = "ev-001",
    kind: EvidenceKind = EvidenceKind.EXCEL,
    payload: dict | None = None,
    received_at: str = "2026-05-11T12:00:00+00:00",
) -> CuratedEvidenceRecord:
    return CuratedEvidenceRecord(
        tenant_id=tenant_id,
        evidence_id=evidence_id,
        kind=kind,
        payload=payload or {"precio_venta": 10.0, "costo_unitario": 20.0},
        source_metadata=BemSourceMetadata(source_name="ventas.xlsx", source_type="excel"),
        received_at=received_at,
    )


@pytest.fixture()
def fake_client() -> FakeSupabaseClient:
    return FakeSupabaseClient()


@pytest.fixture()
def repo(fake_client: FakeSupabaseClient) -> SupabaseCuratedEvidenceRepository:
    return SupabaseCuratedEvidenceRepository(supabase_client=fake_client)


def test_create_upsert_inserta(repo: SupabaseCuratedEvidenceRepository, fake_client: FakeSupabaseClient) -> None:
    repo.create(_make_record())
    rows = fake_client.get_rows("curated_evidence")
    assert len(rows) == 1
    assert rows[0]["tenant_id"] == "tenant-a"
    assert rows[0]["evidence_id"] == "ev-001"


def test_create_upsert_actualiza_existente(repo: SupabaseCuratedEvidenceRepository, fake_client: FakeSupabaseClient) -> None:
    repo.create(_make_record(payload={"precio_venta": 10.0}))
    repo.create(_make_record(payload={"precio_venta": 99.0}))
    rows = fake_client.get_rows("curated_evidence")
    assert len(rows) == 1
    assert rows[0]["payload"]["precio_venta"] == 99.0


def test_save_alias_create(repo: SupabaseCuratedEvidenceRepository, fake_client: FakeSupabaseClient) -> None:
    repo.save(_make_record(evidence_id="ev-save"))
    rows = fake_client.get_rows("curated_evidence")
    assert len(rows) == 1
    assert rows[0]["evidence_id"] == "ev-save"


def test_get_by_evidence_id_filtra_tenant(repo: SupabaseCuratedEvidenceRepository) -> None:
    repo.create(_make_record(tenant_id="tenant-a", evidence_id="ev-shared"))
    repo.create(_make_record(tenant_id="tenant-b", evidence_id="ev-shared"))
    found = repo.get_by_evidence_id("tenant-a", "ev-shared")
    assert found is not None
    assert found.tenant_id == "tenant-a"
    assert found.evidence_id == "ev-shared"


def test_get_by_evidence_id_none_si_no_existe(repo: SupabaseCuratedEvidenceRepository) -> None:
    assert repo.get_by_evidence_id("tenant-a", "ev-none") is None


def test_list_by_tenant_isolation(repo: SupabaseCuratedEvidenceRepository) -> None:
    repo.create(_make_record(tenant_id="tenant-a", evidence_id="ev-1"))
    repo.create(_make_record(tenant_id="tenant-a", evidence_id="ev-2"))
    repo.create(_make_record(tenant_id="tenant-b", evidence_id="ev-3"))
    rows = repo.list_by_tenant("tenant-a")
    assert [r.evidence_id for r in rows] == ["ev-1", "ev-2"]


def test_create_fail_closed_tenant_vacio(repo: SupabaseCuratedEvidenceRepository) -> None:
    with pytest.raises(ValueError, match="tenant_id"):
        repo.create(_make_record(tenant_id=""))


def test_get_fail_closed_tenant_vacio(repo: SupabaseCuratedEvidenceRepository) -> None:
    with pytest.raises(ValueError, match="tenant_id"):
        repo.get_by_evidence_id("", "ev-1")


def test_list_fail_closed_tenant_vacio(repo: SupabaseCuratedEvidenceRepository) -> None:
    with pytest.raises(ValueError, match="tenant_id"):
        repo.list_by_tenant("   ")


def test_create_fail_closed_received_at_invalido(repo: SupabaseCuratedEvidenceRepository) -> None:
    with pytest.raises(ValueError, match="received_at inválido"):
        repo.create(_make_record(received_at="not-a-date"))


def test_row_tenant_mismatch_fail_closed(repo: SupabaseCuratedEvidenceRepository, fake_client: FakeSupabaseClient) -> None:
    repo.create(_make_record(tenant_id="tenant-a", evidence_id="ev-1"))
    rows = fake_client.get_rows("curated_evidence")
    bad_row = dict(rows[0])
    bad_row["tenant_id"] = "tenant-x"
    with pytest.raises(ValueError, match="tenant_id mismatch"):
        repo._row_to_record(bad_row, expected_tenant_id="tenant-a")


def test_sin_cliente_inyectado_y_sin_env_falla_cerrado(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SMARTPYME_SUPABASE_URL", raising=False)
    monkeypatch.delenv("SMARTPYME_SUPABASE_KEY", raising=False)
    with pytest.raises(ValueError, match="BLOCKED_ENVIRONMENT_CONTRACT_MISSING"):
        SupabaseCuratedEvidenceRepository()
