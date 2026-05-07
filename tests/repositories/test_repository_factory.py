"""Tests del factory de repositorios P0 — SmartPyme.

Cubre:
- provider explícito 'supabase' devuelve cada adapter Supabase correcto.
- env SMARTPYME_PERSISTENCE_PROVIDER=supabase devuelve adapter Supabase.
- provider explícito 'sqlite' usa legacy si existe o falla cerrado si no.
- provider inválido falla con error de get_provider.
- tenant-scoped repos fallan cerrado si cliente_id vacío.
- create_cliente_repository no requiere cliente_id.
- supabase_client inyectado se propaga al adapter.
- no network call.
- no regresan tests previos.
"""
import pytest

from app.repositories.repository_factory import (
    create_cliente_repository,
    create_decision_repository,
    create_evidence_candidate_repository,
    create_job_repository,
    create_operational_case_repository,
    create_report_repository,
)


# ---------------------------------------------------------------------------
# FakeSupabaseClient mínimo — sin red
# ---------------------------------------------------------------------------

class _FakeQueryBuilder:
    def __init__(self, store: list) -> None:
        self._store = store
        self._filters: list = []
        self._mode = "select"
        self._insert_row = None

    def select(self, cols="*"):
        self._mode = "select"
        return self

    def insert(self, row):
        self._mode = "insert"
        self._insert_row = row
        return self

    def eq(self, col, val):
        self._filters.append((col, val))
        return self

    def execute(self):
        if self._mode == "insert":
            self._store.append(dict(self._insert_row))
            return _FakeResult([])
        result = list(self._store)
        for col, val in self._filters:
            result = [r for r in result if r.get(col) == val]
        return _FakeResult(result)


class _FakeResult:
    def __init__(self, data):
        self.data = data


class FakeSupabaseClient:
    def __init__(self):
        self._tables: dict = {}

    def table(self, name: str) -> _FakeQueryBuilder:
        if name not in self._tables:
            self._tables[name] = []
        return _FakeQueryBuilder(self._tables[name])


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

CLIENTE_A = "cliente-A"


@pytest.fixture
def fake_client() -> FakeSupabaseClient:
    return FakeSupabaseClient()


@pytest.fixture
def tmp_db(tmp_path):
    """Ruta temporal para SQLite."""
    return tmp_path / "test_factory.db"


# ---------------------------------------------------------------------------
# provider=supabase devuelve adapters Supabase correctos
# ---------------------------------------------------------------------------

def test_create_job_repository_supabase(fake_client):
    from app.repositories.supabase_jobs_repository import SupabaseJobsRepository
    repo = create_job_repository(CLIENTE_A, provider="supabase", supabase_client=fake_client)
    assert isinstance(repo, SupabaseJobsRepository)
    assert repo.cliente_id == CLIENTE_A


def test_create_operational_case_repository_supabase(fake_client):
    from app.repositories.supabase_operational_cases_repository import (
        SupabaseOperationalCasesRepository,
    )
    repo = create_operational_case_repository(
        CLIENTE_A, provider="supabase", supabase_client=fake_client
    )
    assert isinstance(repo, SupabaseOperationalCasesRepository)
    assert repo.cliente_id == CLIENTE_A


def test_create_report_repository_supabase(fake_client):
    from app.repositories.supabase_reports_repository import SupabaseReportsRepository
    repo = create_report_repository(
        CLIENTE_A, provider="supabase", supabase_client=fake_client
    )
    assert isinstance(repo, SupabaseReportsRepository)
    assert repo.cliente_id == CLIENTE_A


def test_create_decision_repository_supabase(fake_client):
    from app.repositories.supabase_decisions_repository import SupabaseDecisionsRepository
    repo = create_decision_repository(
        CLIENTE_A, provider="supabase", supabase_client=fake_client
    )
    assert isinstance(repo, SupabaseDecisionsRepository)
    assert repo.cliente_id == CLIENTE_A


def test_create_evidence_candidate_repository_supabase(fake_client):
    from app.repositories.supabase_evidence_candidates_repository import (
        SupabaseEvidenceCandidatesRepository,
    )
    repo = create_evidence_candidate_repository(
        CLIENTE_A, provider="supabase", supabase_client=fake_client
    )
    assert isinstance(repo, SupabaseEvidenceCandidatesRepository)
    assert repo.cliente_id == CLIENTE_A


def test_create_cliente_repository_supabase(fake_client):
    from app.repositories.supabase_clientes_repository import SupabaseClientesRepository
    repo = create_cliente_repository(provider="supabase", supabase_client=fake_client)
    assert isinstance(repo, SupabaseClientesRepository)


# ---------------------------------------------------------------------------
# env SMARTPYME_PERSISTENCE_PROVIDER=supabase devuelve adapter Supabase
# ---------------------------------------------------------------------------

def test_env_supabase_devuelve_adapter_supabase(monkeypatch, fake_client):
    monkeypatch.setenv("SMARTPYME_PERSISTENCE_PROVIDER", "supabase")
    from app.repositories.supabase_jobs_repository import SupabaseJobsRepository
    repo = create_job_repository(CLIENTE_A, supabase_client=fake_client)
    assert isinstance(repo, SupabaseJobsRepository)


def test_env_supabase_operational_case(monkeypatch, fake_client):
    monkeypatch.setenv("SMARTPYME_PERSISTENCE_PROVIDER", "supabase")
    from app.repositories.supabase_operational_cases_repository import (
        SupabaseOperationalCasesRepository,
    )
    repo = create_operational_case_repository(CLIENTE_A, supabase_client=fake_client)
    assert isinstance(repo, SupabaseOperationalCasesRepository)


# ---------------------------------------------------------------------------
# provider=sqlite usa legacy si existe o falla cerrado si no
# ---------------------------------------------------------------------------

def test_create_job_repository_sqlite(tmp_db):
    from app.repositories.job_repository import JobRepository
    repo = create_job_repository(CLIENTE_A, provider="sqlite", db_path=tmp_db)
    assert isinstance(repo, JobRepository)
    assert repo.cliente_id == CLIENTE_A


def test_create_operational_case_repository_sqlite(tmp_db):
    from app.repositories.operational_case_repository import OperationalCaseRepository
    repo = create_operational_case_repository(CLIENTE_A, provider="sqlite", db_path=tmp_db)
    assert isinstance(repo, OperationalCaseRepository)
    assert repo.cliente_id == CLIENTE_A


def test_create_decision_repository_sqlite_tiene_list_decisions(tmp_db):
    """DecisionRepository SQLite se envuelve con adapter que expone list_decisions()."""
    repo = create_decision_repository(CLIENTE_A, provider="sqlite", db_path=tmp_db)
    assert hasattr(repo, "list_decisions")
    assert callable(repo.list_decisions)


def test_create_decision_repository_sqlite_tiene_create_y_get(tmp_db):
    repo = create_decision_repository(CLIENTE_A, provider="sqlite", db_path=tmp_db)
    assert hasattr(repo, "create")
    assert hasattr(repo, "get")


def test_create_report_repository_sqlite_falla_cerrado():
    """No existe repo SQLite para reports P0 → NotImplementedError."""
    with pytest.raises(NotImplementedError, match="SQLITE_REPOSITORY_NOT_AVAILABLE_FOR_P0_ENTITY"):
        create_report_repository(CLIENTE_A, provider="sqlite", db_path="/tmp/x.db")


def test_create_evidence_candidate_repository_sqlite_falla_cerrado():
    """EvidenceCandidateRepository usa contrato BEM, no P0 → NotImplementedError."""
    with pytest.raises(NotImplementedError, match="SQLITE_REPOSITORY_NOT_AVAILABLE_FOR_P0_ENTITY"):
        create_evidence_candidate_repository(CLIENTE_A, provider="sqlite", db_path="/tmp/x.db")


def test_create_cliente_repository_sqlite_falla_cerrado():
    """No existe repo SQLite de clientes → NotImplementedError."""
    with pytest.raises(NotImplementedError, match="SQLITE_REPOSITORY_NOT_AVAILABLE_FOR_P0_ENTITY"):
        create_cliente_repository(provider="sqlite")


# ---------------------------------------------------------------------------
# provider inválido falla con error de get_provider
# ---------------------------------------------------------------------------

def test_provider_invalido_falla(fake_client):
    with pytest.raises(ValueError, match="PERSISTENCE_PROVIDER_INVALID"):
        create_job_repository(CLIENTE_A, provider="mongo", supabase_client=fake_client)


def test_provider_invalido_en_operational_case(fake_client):
    with pytest.raises(ValueError, match="PERSISTENCE_PROVIDER_INVALID"):
        create_operational_case_repository(CLIENTE_A, provider="redis", supabase_client=fake_client)


# ---------------------------------------------------------------------------
# tenant-scoped repos fallan cerrado si cliente_id vacío
# ---------------------------------------------------------------------------

def test_create_job_repository_cliente_id_vacio(fake_client):
    with pytest.raises(ValueError, match="cliente_id"):
        create_job_repository("", provider="supabase", supabase_client=fake_client)


def test_create_job_repository_cliente_id_espacios(fake_client):
    with pytest.raises(ValueError, match="cliente_id"):
        create_job_repository("   ", provider="supabase", supabase_client=fake_client)


def test_create_operational_case_repository_cliente_id_vacio(fake_client):
    with pytest.raises(ValueError, match="cliente_id"):
        create_operational_case_repository("", provider="supabase", supabase_client=fake_client)


def test_create_report_repository_cliente_id_vacio(fake_client):
    with pytest.raises(ValueError, match="cliente_id"):
        create_report_repository("", provider="supabase", supabase_client=fake_client)


def test_create_decision_repository_cliente_id_vacio(fake_client):
    with pytest.raises(ValueError, match="cliente_id"):
        create_decision_repository("", provider="supabase", supabase_client=fake_client)


def test_create_evidence_candidate_repository_cliente_id_vacio(fake_client):
    with pytest.raises(ValueError, match="cliente_id"):
        create_evidence_candidate_repository("", provider="supabase", supabase_client=fake_client)


# ---------------------------------------------------------------------------
# create_cliente_repository no requiere cliente_id
# ---------------------------------------------------------------------------

def test_create_cliente_repository_no_requiere_cliente_id(fake_client):
    """create_cliente_repository() no toma cliente_id — no debe lanzar."""
    repo = create_cliente_repository(provider="supabase", supabase_client=fake_client)
    assert repo is not None


# ---------------------------------------------------------------------------
# supabase_client inyectado se propaga al adapter
# ---------------------------------------------------------------------------

def test_supabase_client_inyectado_se_propaga_a_jobs(fake_client):
    """El fake_client inyectado es el mismo que usa el adapter internamente."""
    repo = create_job_repository(CLIENTE_A, provider="supabase", supabase_client=fake_client)
    assert repo._client is fake_client


def test_supabase_client_inyectado_se_propaga_a_cases(fake_client):
    repo = create_operational_case_repository(
        CLIENTE_A, provider="supabase", supabase_client=fake_client
    )
    assert repo._client is fake_client


def test_supabase_client_inyectado_se_propaga_a_reports(fake_client):
    repo = create_report_repository(
        CLIENTE_A, provider="supabase", supabase_client=fake_client
    )
    assert repo._client is fake_client


def test_supabase_client_inyectado_se_propaga_a_decisions(fake_client):
    repo = create_decision_repository(
        CLIENTE_A, provider="supabase", supabase_client=fake_client
    )
    assert repo._client is fake_client


def test_supabase_client_inyectado_se_propaga_a_evidence(fake_client):
    repo = create_evidence_candidate_repository(
        CLIENTE_A, provider="supabase", supabase_client=fake_client
    )
    assert repo._client is fake_client


def test_supabase_client_inyectado_se_propaga_a_clientes(fake_client):
    repo = create_cliente_repository(provider="supabase", supabase_client=fake_client)
    assert repo._client is fake_client


# ---------------------------------------------------------------------------
# sqlite requiere db_path — falla si no se provee
# ---------------------------------------------------------------------------

def test_create_job_repository_sqlite_sin_db_path_falla():
    with pytest.raises(ValueError, match="db_path"):
        create_job_repository(CLIENTE_A, provider="sqlite")


def test_create_operational_case_repository_sqlite_sin_db_path_falla():
    with pytest.raises(ValueError, match="db_path"):
        create_operational_case_repository(CLIENTE_A, provider="sqlite")


def test_create_decision_repository_sqlite_sin_db_path_falla():
    with pytest.raises(ValueError, match="db_path"):
        create_decision_repository(CLIENTE_A, provider="sqlite")


# ---------------------------------------------------------------------------
# Sin llamadas de red en ningún test
# ---------------------------------------------------------------------------

def test_no_hay_llamadas_de_red(fake_client):
    """FakeSupabaseClient no hace llamadas de red."""
    repo = create_job_repository(CLIENTE_A, provider="supabase", supabase_client=fake_client)
    assert repo is not None
