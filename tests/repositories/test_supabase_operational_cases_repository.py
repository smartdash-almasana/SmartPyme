"""Tests del adapter Supabase para operational_cases — SmartPyme P0.

Usa FakeSupabaseClient (in-memory, sin red) para probar:
- create_case inserta con cliente_id correcto.
- create_case conserva case_id, job_id, status, payload, metadata.
- get_case filtra por cliente_id y case_id.
- list_cases filtra por cliente_id.
- update_case_status filtra por cliente_id y case_id.
- cliente_id vacío falla cerrado.
- mismatch de cliente_id falla cerrado.
- env incompleta falla solo cuando no se inyecta cliente.
- tests no hacen network call.
- no regresan tests previos.
"""
import pytest

from app.contracts.operational_case import OperationalCase
from app.repositories.supabase_operational_cases_repository import (
    SupabaseOperationalCasesRepository,
)


# ---------------------------------------------------------------------------
# FakeSupabaseClient — cliente in-memory sin red
# ---------------------------------------------------------------------------

class _FakeQueryBuilder:
    """Encadena .select/.insert/.update/.eq/.execute() sobre una lista in-memory."""

    def __init__(self, store: list[dict]) -> None:
        self._store = store
        self._filters: list[tuple[str, object]] = []
        self._mode: str = "select"
        self._insert_row: dict | None = None
        self._update_patch: dict | None = None
        self._select_cols: str = "*"

    def select(self, cols: str = "*") -> "_FakeQueryBuilder":
        self._mode = "select"
        self._select_cols = cols
        return self

    def insert(self, row: dict) -> "_FakeQueryBuilder":
        self._mode = "insert"
        self._insert_row = row
        return self

    def update(self, patch: dict) -> "_FakeQueryBuilder":
        self._mode = "update"
        self._update_patch = patch
        return self

    def eq(self, col: str, val: object) -> "_FakeQueryBuilder":
        self._filters.append((col, val))
        return self

    def execute(self) -> "_FakeResult":
        if self._mode == "insert":
            self._store.append(dict(self._insert_row))
            return _FakeResult([])

        if self._mode == "update":
            updated = []
            for row in self._store:
                match = all(row.get(col) == val for col, val in self._filters)
                if match:
                    row.update(self._update_patch)
                    updated.append(dict(row))
            return _FakeResult(updated)

        # select with filters
        result = list(self._store)
        for col, val in self._filters:
            result = [r for r in result if r.get(col) == val]
        return _FakeResult(result)


class _FakeResult:
    def __init__(self, data: list[dict]) -> None:
        self.data = data


class FakeSupabaseClient:
    """Cliente Supabase in-memory. Sin red. Aislado por instancia."""

    def __init__(self) -> None:
        self._tables: dict[str, list[dict]] = {}

    def table(self, name: str) -> _FakeQueryBuilder:
        if name not in self._tables:
            self._tables[name] = []
        return _FakeQueryBuilder(self._tables[name])

    def get_rows(self, table: str) -> list[dict]:
        """Helper de test para inspeccionar el estado interno."""
        return list(self._tables.get(table, []))


# ---------------------------------------------------------------------------
# Fixtures y helpers
# ---------------------------------------------------------------------------

CLIENTE_A = "cliente-A"
CLIENTE_B = "cliente-B"

_VALID_HYPOTHESIS = "Investigar si el margen bruto está por debajo del umbral esperado"


def _make_case(
    case_id: str = "case-001",
    cliente_id: str = CLIENTE_A,
    job_id: str = "job-001",
    skill_id: str = "analisis_comercial",
    hypothesis: str = _VALID_HYPOTHESIS,
    status: str = "OPEN",
    evidence_ids: list[str] | None = None,
) -> OperationalCase:
    return OperationalCase(
        case_id=case_id,
        cliente_id=cliente_id,
        job_id=job_id,
        skill_id=skill_id,
        hypothesis=hypothesis,
        status=status,
        evidence_ids=evidence_ids or [],
    )


@pytest.fixture
def fake_client() -> FakeSupabaseClient:
    return FakeSupabaseClient()


@pytest.fixture
def repo(fake_client: FakeSupabaseClient) -> SupabaseOperationalCasesRepository:
    return SupabaseOperationalCasesRepository(
        cliente_id=CLIENTE_A, supabase_client=fake_client
    )


# ---------------------------------------------------------------------------
# cliente_id vacío falla cerrado
# ---------------------------------------------------------------------------

def test_cliente_id_vacio_lanza_error(fake_client):
    with pytest.raises(ValueError, match="cliente_id"):
        SupabaseOperationalCasesRepository(cliente_id="", supabase_client=fake_client)


def test_cliente_id_solo_espacios_lanza_error(fake_client):
    with pytest.raises(ValueError, match="cliente_id"):
        SupabaseOperationalCasesRepository(
            cliente_id="   ", supabase_client=fake_client
        )


# ---------------------------------------------------------------------------
# env incompleta falla solo cuando no se inyecta cliente
# ---------------------------------------------------------------------------

def test_sin_cliente_inyectado_y_sin_env_falla_cerrado(monkeypatch):
    """Sin cliente inyectado y sin env Supabase → BLOCKED_ENVIRONMENT_CONTRACT_MISSING."""
    monkeypatch.delenv("SMARTPYME_SUPABASE_URL", raising=False)
    monkeypatch.delenv("SMARTPYME_SUPABASE_KEY", raising=False)
    with pytest.raises(ValueError, match="BLOCKED_ENVIRONMENT_CONTRACT_MISSING"):
        SupabaseOperationalCasesRepository(cliente_id=CLIENTE_A)


def test_con_cliente_inyectado_no_requiere_env(monkeypatch, fake_client):
    """Con cliente inyectado, no se valida el entorno Supabase."""
    monkeypatch.delenv("SMARTPYME_SUPABASE_URL", raising=False)
    monkeypatch.delenv("SMARTPYME_SUPABASE_KEY", raising=False)
    repo = SupabaseOperationalCasesRepository(
        cliente_id=CLIENTE_A, supabase_client=fake_client
    )
    assert repo.cliente_id == CLIENTE_A


# ---------------------------------------------------------------------------
# create_case — inserta con cliente_id correcto
# ---------------------------------------------------------------------------

def test_create_case_inserta_fila(repo, fake_client):
    case = _make_case()
    repo.create_case(case)
    rows = fake_client.get_rows("operational_cases")
    assert len(rows) == 1
    assert rows[0]["case_id"] == "case-001"
    assert rows[0]["cliente_id"] == CLIENTE_A


def test_create_case_conserva_case_id(repo, fake_client):
    case = _make_case(case_id="case-xyz")
    repo.create_case(case)
    rows = fake_client.get_rows("operational_cases")
    assert rows[0]["case_id"] == "case-xyz"


def test_create_case_conserva_job_id(repo, fake_client):
    case = _make_case(job_id="job-999")
    repo.create_case(case)
    rows = fake_client.get_rows("operational_cases")
    assert rows[0]["job_id"] == "job-999"


def test_create_case_conserva_status(repo, fake_client):
    case = _make_case(status="OPEN")
    repo.create_case(case)
    rows = fake_client.get_rows("operational_cases")
    assert rows[0]["status"] == "OPEN"


def test_create_case_payload_es_dict_no_string(repo, fake_client):
    """payload se inserta como dict, no como string."""
    case = _make_case(evidence_ids=["ev-1", "ev-2"])
    repo.create_case(case)
    rows = fake_client.get_rows("operational_cases")
    assert isinstance(rows[0]["payload"], dict)


def test_create_case_payload_contiene_evidence_ids(repo, fake_client):
    case = _make_case(evidence_ids=["ev-1", "ev-2"])
    repo.create_case(case)
    rows = fake_client.get_rows("operational_cases")
    assert rows[0]["payload"]["evidence_ids"] == ["ev-1", "ev-2"]


def test_create_case_metadata_es_dict(repo, fake_client):
    """metadata se inserta como dict."""
    case = _make_case()
    repo.create_case(case)
    rows = fake_client.get_rows("operational_cases")
    assert isinstance(rows[0]["metadata"], dict)


def test_create_case_mismatch_cliente_id_falla_cerrado(repo):
    """create_case() rechaza caso con cliente_id diferente al del repo."""
    case = _make_case(cliente_id=CLIENTE_B)
    with pytest.raises(ValueError, match="cliente_id mismatch"):
        repo.create_case(case)


def test_create_case_no_inserta_en_mismatch(repo, fake_client):
    """Tras mismatch, la tabla queda vacía."""
    case = _make_case(cliente_id=CLIENTE_B)
    with pytest.raises(ValueError):
        repo.create_case(case)
    assert fake_client.get_rows("operational_cases") == []


# ---------------------------------------------------------------------------
# get_case — filtra por cliente_id y case_id
# ---------------------------------------------------------------------------

def test_get_case_retorna_caso_existente(repo):
    case = _make_case()
    repo.create_case(case)
    fetched = repo.get_case("case-001")
    assert fetched is not None
    assert fetched.case_id == "case-001"
    assert fetched.cliente_id == CLIENTE_A


def test_get_case_retorna_none_si_no_existe(repo):
    fetched = repo.get_case("case-inexistente")
    assert fetched is None


def test_get_case_no_retorna_caso_de_otro_cliente(fake_client):
    """get_case() no retorna casos de otro cliente aunque compartan case_id."""
    repo_a = SupabaseOperationalCasesRepository(
        cliente_id=CLIENTE_A, supabase_client=fake_client
    )
    repo_b = SupabaseOperationalCasesRepository(
        cliente_id=CLIENTE_B, supabase_client=fake_client
    )

    case_a = _make_case(case_id="case-shared", cliente_id=CLIENTE_A)
    repo_a.create_case(case_a)

    assert repo_b.get_case("case-shared") is None


def test_get_case_preserva_job_id(repo):
    case = _make_case(job_id="job-abc")
    repo.create_case(case)
    fetched = repo.get_case("case-001")
    assert fetched.job_id == "job-abc"


def test_get_case_preserva_status(repo):
    case = _make_case(status="OPEN")
    repo.create_case(case)
    fetched = repo.get_case("case-001")
    assert fetched.status == "OPEN"


def test_get_case_preserva_evidence_ids(repo):
    case = _make_case(evidence_ids=["ev-1", "ev-2"])
    repo.create_case(case)
    fetched = repo.get_case("case-001")
    assert fetched.evidence_ids == ["ev-1", "ev-2"]


# ---------------------------------------------------------------------------
# list_cases — filtra por cliente_id
# ---------------------------------------------------------------------------

def test_list_cases_retorna_casos_del_cliente(repo):
    repo.create_case(_make_case(case_id="case-001"))
    repo.create_case(_make_case(case_id="case-002"))
    cases = repo.list_cases()
    assert len(cases) == 2
    assert all(c.cliente_id == CLIENTE_A for c in cases)


def test_list_cases_vacio_si_no_hay_casos(repo):
    assert repo.list_cases() == []


def test_list_cases_aislamiento_multi_cliente(fake_client):
    """list_cases() nunca retorna casos de otro cliente."""
    repo_a = SupabaseOperationalCasesRepository(
        cliente_id=CLIENTE_A, supabase_client=fake_client
    )
    repo_b = SupabaseOperationalCasesRepository(
        cliente_id=CLIENTE_B, supabase_client=fake_client
    )

    repo_a.create_case(_make_case(case_id="case-A1", cliente_id=CLIENTE_A))
    repo_a.create_case(_make_case(case_id="case-A2", cliente_id=CLIENTE_A))
    repo_b.create_case(_make_case(case_id="case-B1", cliente_id=CLIENTE_B))

    cases_a = repo_a.list_cases()
    cases_b = repo_b.list_cases()

    assert len(cases_a) == 2
    assert all(c.cliente_id == CLIENTE_A for c in cases_a)

    assert len(cases_b) == 1
    assert cases_b[0].case_id == "case-B1"
    assert cases_b[0].cliente_id == CLIENTE_B


# ---------------------------------------------------------------------------
# update_case_status — filtra por cliente_id y case_id
# ---------------------------------------------------------------------------

def test_update_case_status_actualiza_estado(repo, fake_client):
    repo.create_case(_make_case(status="OPEN"))
    result = repo.update_case_status("case-001", "BLOCKED")
    assert result is True
    rows = fake_client.get_rows("operational_cases")
    assert rows[0]["status"] == "BLOCKED"


def test_update_case_status_retorna_false_si_no_existe(repo):
    result = repo.update_case_status("case-inexistente", "BLOCKED")
    assert result is False


def test_update_case_status_no_afecta_otro_cliente(fake_client):
    """update_case_status() no modifica casos de otro cliente."""
    repo_a = SupabaseOperationalCasesRepository(
        cliente_id=CLIENTE_A, supabase_client=fake_client
    )
    repo_b = SupabaseOperationalCasesRepository(
        cliente_id=CLIENTE_B, supabase_client=fake_client
    )

    repo_a.create_case(_make_case(case_id="case-shared", cliente_id=CLIENTE_A))

    # repo_b intenta actualizar un case_id que existe pero pertenece a repo_a
    result = repo_b.update_case_status("case-shared", "CLOSED")
    assert result is False

    # El caso de repo_a no fue modificado
    fetched = repo_a.get_case("case-shared")
    assert fetched.status == "OPEN"


def test_update_case_status_filtra_por_case_id(repo, fake_client):
    """update_case_status() solo actualiza el case_id correcto."""
    repo.create_case(_make_case(case_id="case-001", status="OPEN"))
    repo.create_case(_make_case(case_id="case-002", status="OPEN"))

    repo.update_case_status("case-001", "CLOSED")

    rows = fake_client.get_rows("operational_cases")
    statuses = {r["case_id"]: r["status"] for r in rows}
    assert statuses["case-001"] == "CLOSED"
    assert statuses["case-002"] == "OPEN"


# ---------------------------------------------------------------------------
# OperationalCasePort protocol compliance
# ---------------------------------------------------------------------------

def test_supabase_operational_cases_repository_satisface_port(fake_client):
    """SupabaseOperationalCasesRepository satisface el protocolo OperationalCasePort."""
    from app.repositories.persistence_ports import OperationalCasePort

    repo = SupabaseOperationalCasesRepository(
        cliente_id=CLIENTE_A, supabase_client=fake_client
    )
    assert isinstance(repo, OperationalCasePort)


# ---------------------------------------------------------------------------
# Sin llamadas de red en ningún test
# ---------------------------------------------------------------------------

def test_no_hay_llamadas_de_red(repo):
    """FakeSupabaseClient no hace llamadas de red — verificar que el repo usa el fake."""
    case = _make_case()
    repo.create_case(case)
    fetched = repo.get_case("case-001")
    assert fetched is not None
