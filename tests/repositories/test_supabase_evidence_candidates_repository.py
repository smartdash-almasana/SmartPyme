"""Tests del adapter Supabase para evidence_candidates — SmartPyme P0.

Usa FakeSupabaseClient (in-memory, sin red) para probar:
- create inserta con cliente_id correcto.
- create conserva evidence_id, job_id, evidence_type, payload, metadata, status.
- get filtra por cliente_id y evidence_id.
- get no filtra cruzado entre clientes.
- list_by_job filtra por cliente_id y job_id.
- cliente_id vacío falla cerrado.
- mismatch de cliente_id falla cerrado.
- env incompleta falla solo cuando no se inyecta cliente.
- tests no hacen network call.
- no regresan tests previos.
- protocol compliance con EvidenceCandidatePort.
"""
import pytest

from app.contracts.evidence_contract import EvidenceChunk
from app.repositories.supabase_evidence_candidates_repository import (
    SupabaseEvidenceCandidatesRepository,
)


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
# Fixtures y helpers
# ---------------------------------------------------------------------------

CLIENTE_A = "cliente-A"
CLIENTE_B = "cliente-B"


def _make_chunk(
    evidence_id: str = "ev-001",
    cliente_id: str = CLIENTE_A,
    document_id: str = "doc-001",
    raw_document_id: str | None = "raw-001",
    job_id: str | None = "job-001",
    plan_id: str | None = None,
    filename: str = "ventas_2026.csv",
    page: int = 1,
    text: str = "Ventas totales: $150,000",
    chunk_order: int = 0,
    metadata: dict | None = None,
) -> EvidenceChunk:
    return EvidenceChunk(
        evidence_id=evidence_id,
        cliente_id=cliente_id,
        document_id=document_id,
        raw_document_id=raw_document_id,
        job_id=job_id,
        plan_id=plan_id,
        filename=filename,
        page=page,
        text=text,
        chunk_order=chunk_order,
        metadata=metadata or {},
    )


@pytest.fixture
def fake_client() -> FakeSupabaseClient:
    return FakeSupabaseClient()


@pytest.fixture
def repo(fake_client: FakeSupabaseClient) -> SupabaseEvidenceCandidatesRepository:
    return SupabaseEvidenceCandidatesRepository(
        cliente_id=CLIENTE_A, supabase_client=fake_client
    )


# ---------------------------------------------------------------------------
# cliente_id vacío falla cerrado
# ---------------------------------------------------------------------------

def test_cliente_id_vacio_lanza_error(fake_client):
    with pytest.raises(ValueError, match="cliente_id"):
        SupabaseEvidenceCandidatesRepository(cliente_id="", supabase_client=fake_client)


def test_cliente_id_solo_espacios_lanza_error(fake_client):
    with pytest.raises(ValueError, match="cliente_id"):
        SupabaseEvidenceCandidatesRepository(
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
        SupabaseEvidenceCandidatesRepository(cliente_id=CLIENTE_A)


def test_con_cliente_inyectado_no_requiere_env(monkeypatch, fake_client):
    """Con cliente inyectado, no se valida el entorno Supabase."""
    monkeypatch.delenv("SMARTPYME_SUPABASE_URL", raising=False)
    monkeypatch.delenv("SMARTPYME_SUPABASE_KEY", raising=False)
    repo = SupabaseEvidenceCandidatesRepository(
        cliente_id=CLIENTE_A, supabase_client=fake_client
    )
    assert repo.cliente_id == CLIENTE_A


# ---------------------------------------------------------------------------
# create — inserta con cliente_id correcto
# ---------------------------------------------------------------------------

def test_create_inserta_fila(repo, fake_client):
    chunk = _make_chunk()
    repo.create(chunk)
    rows = fake_client.get_rows("evidence_candidates")
    assert len(rows) == 1
    assert rows[0]["evidence_id"] == "ev-001"
    assert rows[0]["cliente_id"] == CLIENTE_A


def test_create_conserva_evidence_id(repo, fake_client):
    chunk = _make_chunk(evidence_id="ev-xyz")
    repo.create(chunk)
    rows = fake_client.get_rows("evidence_candidates")
    assert rows[0]["evidence_id"] == "ev-xyz"


def test_create_conserva_job_id(repo, fake_client):
    chunk = _make_chunk(job_id="job-999")
    repo.create(chunk)
    rows = fake_client.get_rows("evidence_candidates")
    assert rows[0]["job_id"] == "job-999"


def test_create_job_id_none_se_almacena_como_none(repo, fake_client):
    chunk = _make_chunk(job_id=None)
    repo.create(chunk)
    rows = fake_client.get_rows("evidence_candidates")
    assert rows[0]["job_id"] is None


def test_create_evidence_type_es_chunk(repo, fake_client):
    """evidence_type se fija como 'chunk' para EvidenceChunk."""
    chunk = _make_chunk()
    repo.create(chunk)
    rows = fake_client.get_rows("evidence_candidates")
    assert rows[0]["evidence_type"] == "chunk"


def test_create_status_es_candidate(repo, fake_client):
    """status se fija como 'candidate' por defecto."""
    chunk = _make_chunk()
    repo.create(chunk)
    rows = fake_client.get_rows("evidence_candidates")
    assert rows[0]["status"] == "candidate"


def test_create_payload_es_dict_no_string(repo, fake_client):
    """payload se inserta como dict, no como string."""
    chunk = _make_chunk()
    repo.create(chunk)
    rows = fake_client.get_rows("evidence_candidates")
    assert isinstance(rows[0]["payload"], dict)


def test_create_payload_contiene_text(repo, fake_client):
    chunk = _make_chunk(text="Costo de ventas: $90,000")
    repo.create(chunk)
    rows = fake_client.get_rows("evidence_candidates")
    assert rows[0]["payload"]["text"] == "Costo de ventas: $90,000"


def test_create_payload_contiene_filename(repo, fake_client):
    chunk = _make_chunk(filename="compras_q1.xlsx")
    repo.create(chunk)
    rows = fake_client.get_rows("evidence_candidates")
    assert rows[0]["payload"]["filename"] == "compras_q1.xlsx"


def test_create_payload_contiene_page_y_chunk_order(repo, fake_client):
    chunk = _make_chunk(page=3, chunk_order=7)
    repo.create(chunk)
    rows = fake_client.get_rows("evidence_candidates")
    assert rows[0]["payload"]["page"] == 3
    assert rows[0]["payload"]["chunk_order"] == 7


def test_create_metadata_es_dict(repo, fake_client):
    """metadata se inserta como dict."""
    chunk = _make_chunk(metadata={"fuente": "ERP", "confianza": 0.9})
    repo.create(chunk)
    rows = fake_client.get_rows("evidence_candidates")
    assert isinstance(rows[0]["metadata"], dict)
    assert rows[0]["metadata"]["fuente"] == "ERP"


def test_create_result_es_none_por_defecto(repo, fake_client):
    chunk = _make_chunk()
    repo.create(chunk)
    rows = fake_client.get_rows("evidence_candidates")
    assert rows[0]["result"] is None


def test_create_score_es_none_por_defecto(repo, fake_client):
    """score es None para EvidenceChunk (no tiene score propio)."""
    chunk = _make_chunk()
    repo.create(chunk)
    rows = fake_client.get_rows("evidence_candidates")
    assert rows[0]["score"] is None


def test_create_mismatch_cliente_id_falla_cerrado(repo):
    """create() rechaza chunk con cliente_id diferente al del repo."""
    chunk = _make_chunk(cliente_id=CLIENTE_B)
    with pytest.raises(ValueError, match="cliente_id mismatch"):
        repo.create(chunk)


def test_create_no_inserta_en_mismatch(repo, fake_client):
    """Tras mismatch, la tabla queda vacía."""
    chunk = _make_chunk(cliente_id=CLIENTE_B)
    with pytest.raises(ValueError):
        repo.create(chunk)
    assert fake_client.get_rows("evidence_candidates") == []


# ---------------------------------------------------------------------------
# get — filtra por cliente_id y evidence_id
# ---------------------------------------------------------------------------

def test_get_retorna_chunk_existente(repo):
    chunk = _make_chunk()
    repo.create(chunk)
    fetched = repo.get("ev-001")
    assert fetched is not None
    assert fetched.evidence_id == "ev-001"
    assert fetched.cliente_id == CLIENTE_A


def test_get_retorna_none_si_no_existe(repo):
    fetched = repo.get("ev-inexistente")
    assert fetched is None


def test_get_no_retorna_chunk_de_otro_cliente(fake_client):
    """get() no retorna chunks de otro cliente aunque compartan evidence_id."""
    repo_a = SupabaseEvidenceCandidatesRepository(
        cliente_id=CLIENTE_A, supabase_client=fake_client
    )
    repo_b = SupabaseEvidenceCandidatesRepository(
        cliente_id=CLIENTE_B, supabase_client=fake_client
    )

    chunk_a = _make_chunk(evidence_id="ev-shared", cliente_id=CLIENTE_A)
    repo_a.create(chunk_a)

    assert repo_b.get("ev-shared") is None


def test_get_preserva_job_id(repo):
    chunk = _make_chunk(job_id="job-abc")
    repo.create(chunk)
    fetched = repo.get("ev-001")
    assert fetched.job_id == "job-abc"


def test_get_preserva_text(repo):
    chunk = _make_chunk(text="Margen bruto: 18%")
    repo.create(chunk)
    fetched = repo.get("ev-001")
    assert fetched.text == "Margen bruto: 18%"


def test_get_preserva_filename(repo):
    chunk = _make_chunk(filename="stock_dic.csv")
    repo.create(chunk)
    fetched = repo.get("ev-001")
    assert fetched.filename == "stock_dic.csv"


def test_get_preserva_page_y_chunk_order(repo):
    chunk = _make_chunk(page=5, chunk_order=2)
    repo.create(chunk)
    fetched = repo.get("ev-001")
    assert fetched.page == 5
    assert fetched.chunk_order == 2


def test_get_preserva_metadata(repo):
    chunk = _make_chunk(metadata={"origen": "factura", "periodo": "Q1"})
    repo.create(chunk)
    fetched = repo.get("ev-001")
    assert fetched.metadata.get("origen") == "factura"
    assert fetched.metadata.get("periodo") == "Q1"


# ---------------------------------------------------------------------------
# list_by_job — filtra por cliente_id y job_id
# ---------------------------------------------------------------------------

def test_list_by_job_retorna_chunks_del_job(repo):
    repo.create(_make_chunk(evidence_id="ev-001", job_id="job-A"))
    repo.create(_make_chunk(evidence_id="ev-002", job_id="job-A"))
    repo.create(_make_chunk(evidence_id="ev-003", job_id="job-B"))
    chunks = repo.list_by_job("job-A")
    assert len(chunks) == 2
    assert all(c.job_id == "job-A" for c in chunks)


def test_list_by_job_vacio_si_no_hay_chunks(repo):
    assert repo.list_by_job("job-inexistente") == []


def test_list_by_job_aislamiento_multi_cliente(fake_client):
    """list_by_job() nunca retorna chunks de otro cliente."""
    repo_a = SupabaseEvidenceCandidatesRepository(
        cliente_id=CLIENTE_A, supabase_client=fake_client
    )
    repo_b = SupabaseEvidenceCandidatesRepository(
        cliente_id=CLIENTE_B, supabase_client=fake_client
    )

    repo_a.create(_make_chunk(evidence_id="ev-A1", cliente_id=CLIENTE_A, job_id="job-X"))
    repo_a.create(_make_chunk(evidence_id="ev-A2", cliente_id=CLIENTE_A, job_id="job-X"))
    repo_b.create(_make_chunk(evidence_id="ev-B1", cliente_id=CLIENTE_B, job_id="job-X"))

    chunks_a = repo_a.list_by_job("job-X")
    chunks_b = repo_b.list_by_job("job-X")

    assert len(chunks_a) == 2
    assert all(c.cliente_id == CLIENTE_A for c in chunks_a)

    assert len(chunks_b) == 1
    assert chunks_b[0].evidence_id == "ev-B1"
    assert chunks_b[0].cliente_id == CLIENTE_B


def test_list_by_job_no_mezcla_jobs(repo):
    """list_by_job() solo retorna chunks del job_id solicitado."""
    repo.create(_make_chunk(evidence_id="ev-001", job_id="job-A"))
    repo.create(_make_chunk(evidence_id="ev-002", job_id="job-B"))
    chunks = repo.list_by_job("job-A")
    assert len(chunks) == 1
    assert chunks[0].evidence_id == "ev-001"


# ---------------------------------------------------------------------------
# EvidenceCandidatePort protocol compliance
# ---------------------------------------------------------------------------

def test_supabase_evidence_candidates_repository_satisface_port(fake_client):
    """SupabaseEvidenceCandidatesRepository satisface el protocolo EvidenceCandidatePort."""
    from app.repositories.persistence_ports import EvidenceCandidatePort

    repo = SupabaseEvidenceCandidatesRepository(
        cliente_id=CLIENTE_A, supabase_client=fake_client
    )
    assert isinstance(repo, EvidenceCandidatePort)


# ---------------------------------------------------------------------------
# Sin llamadas de red en ningún test
# ---------------------------------------------------------------------------

def test_no_hay_llamadas_de_red(repo):
    """FakeSupabaseClient no hace llamadas de red — verificar que el repo usa el fake."""
    chunk = _make_chunk()
    repo.create(chunk)
    fetched = repo.get("ev-001")
    assert fetched is not None
