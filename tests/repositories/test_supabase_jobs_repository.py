"""Tests del adapter Supabase para jobs — SmartPyme P0.

Usa FakeSupabaseClient (in-memory, sin red) para probar:
- create inserta con cliente_id correcto.
- get filtra por cliente_id y job_id.
- list_jobs filtra por cliente_id.
- cliente_id vacío falla cerrado.
- cliente_id mismatch falla cerrado.
- env incompleta falla solo cuando no se inyecta cliente.
- no se realiza ninguna llamada de red.
"""
import pytest

from app.contracts.job_contract import Job, JobStatus
from app.repositories.supabase_jobs_repository import SupabaseJobsRepository


# ---------------------------------------------------------------------------
# FakeSupabaseClient — cliente in-memory sin red
# ---------------------------------------------------------------------------

class _FakeQueryBuilder:
    """Encadena .select/.insert/.eq/.execute() sobre una lista in-memory."""

    def __init__(self, store: list[dict]) -> None:
        self._store = store
        self._filters: list[tuple[str, object]] = []
        self._mode: str = "select"
        self._insert_row: dict | None = None
        self._select_cols: str = "*"

    def select(self, cols: str = "*") -> "_FakeQueryBuilder":
        self._mode = "select"
        self._select_cols = cols
        return self

    def insert(self, row: dict) -> "_FakeQueryBuilder":
        self._mode = "insert"
        self._insert_row = row
        return self

    def eq(self, col: str, val: object) -> "_FakeQueryBuilder":
        self._filters.append((col, val))
        return self

    def execute(self) -> "_FakeResult":
        if self._mode == "insert":
            self._store.append(dict(self._insert_row))
            return _FakeResult([])

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
# Fixtures
# ---------------------------------------------------------------------------

CLIENTE_A = "cliente-A"
CLIENTE_B = "cliente-B"


def _make_job(
    job_id: str = "job-001",
    cliente_id: str = CLIENTE_A,
    job_type: str = "diagnostico",
    status: JobStatus = JobStatus.PENDING,
) -> Job:
    return Job(
        job_id=job_id,
        cliente_id=cliente_id,
        job_type=job_type,
        status=status,
        payload={"key": "value"},
        traceable_origin={"source": "test"},
    )


@pytest.fixture
def fake_client() -> FakeSupabaseClient:
    return FakeSupabaseClient()


@pytest.fixture
def repo(fake_client: FakeSupabaseClient) -> SupabaseJobsRepository:
    return SupabaseJobsRepository(cliente_id=CLIENTE_A, supabase_client=fake_client)


# ---------------------------------------------------------------------------
# cliente_id vacío falla cerrado
# ---------------------------------------------------------------------------

def test_cliente_id_vacio_lanza_error(fake_client):
    with pytest.raises(ValueError, match="cliente_id"):
        SupabaseJobsRepository(cliente_id="", supabase_client=fake_client)


def test_cliente_id_solo_espacios_lanza_error(fake_client):
    with pytest.raises(ValueError, match="cliente_id"):
        SupabaseJobsRepository(cliente_id="   ", supabase_client=fake_client)


# ---------------------------------------------------------------------------
# env incompleta falla solo cuando no se inyecta cliente
# ---------------------------------------------------------------------------

def test_sin_cliente_inyectado_y_sin_env_falla_cerrado(monkeypatch):
    """Sin cliente inyectado y sin env Supabase → BLOCKED_ENVIRONMENT_CONTRACT_MISSING."""
    monkeypatch.delenv("SMARTPYME_SUPABASE_URL", raising=False)
    monkeypatch.delenv("SMARTPYME_SUPABASE_KEY", raising=False)
    with pytest.raises(ValueError, match="BLOCKED_ENVIRONMENT_CONTRACT_MISSING"):
        SupabaseJobsRepository(cliente_id=CLIENTE_A)


def test_con_cliente_inyectado_no_requiere_env(monkeypatch, fake_client):
    """Con cliente inyectado, no se valida el entorno Supabase."""
    monkeypatch.delenv("SMARTPYME_SUPABASE_URL", raising=False)
    monkeypatch.delenv("SMARTPYME_SUPABASE_KEY", raising=False)
    # No debe lanzar
    repo = SupabaseJobsRepository(cliente_id=CLIENTE_A, supabase_client=fake_client)
    assert repo.cliente_id == CLIENTE_A


# ---------------------------------------------------------------------------
# create — inserta con cliente_id correcto
# ---------------------------------------------------------------------------

def test_create_inserta_job(repo, fake_client):
    job = _make_job()
    repo.create(job)
    rows = fake_client.get_rows("background_jobs")
    assert len(rows) == 1
    assert rows[0]["job_id"] == "job-001"
    assert rows[0]["cliente_id"] == CLIENTE_A


def test_create_inserta_payload_como_dict(repo, fake_client):
    """payload y traceable_origin se insertan como dict, no como string."""
    job = _make_job()
    repo.create(job)
    rows = fake_client.get_rows("background_jobs")
    assert isinstance(rows[0]["payload"], dict)
    assert isinstance(rows[0]["traceable_origin"], dict)


def test_create_inserta_status_como_string(repo, fake_client):
    """status se inserta como string."""
    job = _make_job(status=JobStatus.RUNNING)
    repo.create(job)
    rows = fake_client.get_rows("background_jobs")
    assert rows[0]["status"] == "RUNNING"


def test_create_mismatch_cliente_id_falla_cerrado(repo):
    """create() rechaza job con cliente_id diferente al del repo."""
    job = _make_job(cliente_id=CLIENTE_B)
    with pytest.raises(ValueError, match="cliente_id mismatch"):
        repo.create(job)


def test_create_no_inserta_en_mismatch(repo, fake_client):
    """Tras mismatch, la tabla queda vacía."""
    job = _make_job(cliente_id=CLIENTE_B)
    with pytest.raises(ValueError):
        repo.create(job)
    assert fake_client.get_rows("background_jobs") == []


# ---------------------------------------------------------------------------
# get — filtra por cliente_id y job_id
# ---------------------------------------------------------------------------

def test_get_retorna_job_existente(repo):
    job = _make_job()
    repo.create(job)
    fetched = repo.get("job-001")
    assert fetched is not None
    assert fetched.job_id == "job-001"
    assert fetched.cliente_id == CLIENTE_A


def test_get_retorna_none_si_no_existe(repo):
    fetched = repo.get("job-inexistente")
    assert fetched is None


def test_get_no_retorna_job_de_otro_cliente(fake_client):
    """get() no retorna jobs de otro cliente aunque compartan job_id."""
    repo_a = SupabaseJobsRepository(cliente_id=CLIENTE_A, supabase_client=fake_client)
    repo_b = SupabaseJobsRepository(cliente_id=CLIENTE_B, supabase_client=fake_client)

    job_a = _make_job(job_id="job-shared", cliente_id=CLIENTE_A)
    repo_a.create(job_a)

    # repo_b no debe ver el job de repo_a
    assert repo_b.get("job-shared") is None


def test_get_preserva_payload_como_dict(repo):
    job = _make_job()
    repo.create(job)
    fetched = repo.get("job-001")
    assert isinstance(fetched.payload, dict)
    assert fetched.payload == {"key": "value"}


def test_get_preserva_status(repo):
    job = _make_job(status=JobStatus.RUNNING)
    repo.create(job)
    fetched = repo.get("job-001")
    assert fetched.status == JobStatus.RUNNING


# ---------------------------------------------------------------------------
# list_jobs — filtra por cliente_id
# ---------------------------------------------------------------------------

def test_list_jobs_retorna_jobs_del_cliente(repo):
    repo.create(_make_job(job_id="job-001"))
    repo.create(_make_job(job_id="job-002"))
    jobs = repo.list_jobs()
    assert len(jobs) == 2
    assert all(j.cliente_id == CLIENTE_A for j in jobs)


def test_list_jobs_vacio_si_no_hay_jobs(repo):
    assert repo.list_jobs() == []


def test_list_jobs_aislamiento_multi_cliente(fake_client):
    """list_jobs() nunca retorna jobs de otro cliente."""
    repo_a = SupabaseJobsRepository(cliente_id=CLIENTE_A, supabase_client=fake_client)
    repo_b = SupabaseJobsRepository(cliente_id=CLIENTE_B, supabase_client=fake_client)

    repo_a.create(_make_job(job_id="job-A1", cliente_id=CLIENTE_A))
    repo_a.create(_make_job(job_id="job-A2", cliente_id=CLIENTE_A))
    repo_b.create(_make_job(job_id="job-B1", cliente_id=CLIENTE_B))

    jobs_a = repo_a.list_jobs()
    jobs_b = repo_b.list_jobs()

    assert len(jobs_a) == 2
    assert all(j.cliente_id == CLIENTE_A for j in jobs_a)

    assert len(jobs_b) == 1
    assert jobs_b[0].job_id == "job-B1"
    assert jobs_b[0].cliente_id == CLIENTE_B


# ---------------------------------------------------------------------------
# JobPort protocol compliance
# ---------------------------------------------------------------------------

def test_supabase_jobs_repository_satisface_job_port(fake_client):
    """SupabaseJobsRepository satisface el protocolo JobPort."""
    from app.repositories.persistence_ports import JobPort
    repo = SupabaseJobsRepository(cliente_id=CLIENTE_A, supabase_client=fake_client)
    assert isinstance(repo, JobPort)


# ---------------------------------------------------------------------------
# Sin llamadas de red en ningún test
# ---------------------------------------------------------------------------

def test_no_hay_llamadas_de_red(repo):
    """FakeSupabaseClient no hace llamadas de red — verificar que el repo usa el fake."""
    # Si el repo usara red real, este test fallaría por timeout o ImportError.
    # El hecho de que llegue aquí sin error confirma que usa el fake.
    job = _make_job()
    repo.create(job)
    fetched = repo.get("job-001")
    assert fetched is not None
