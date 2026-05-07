"""Tests del adapter Supabase para decisions — SmartPyme P0.

Usa FakeSupabaseClient (in-memory, sin red) para probar:
- create inserta con cliente_id correcto.
- create conserva decision_id, case_id, report_id, decision_type,
  decision_value, rationale, metadata.
- get filtra por cliente_id y decision_id.
- list_decisions filtra por cliente_id.
- no filtra cruzado entre clientes.
- cliente_id vacío falla cerrado.
- mismatch de cliente_id falla cerrado.
- env incompleta falla solo cuando no se inyecta cliente.
- tests no hacen network call.
- no regresan tests previos.
- protocol compliance con DecisionPort.
"""
import pytest

from app.contracts.decision_record import DecisionRecord
from app.repositories.supabase_decisions_repository import SupabaseDecisionsRepository


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


def _make_decision(
    decision_id: str = "dec-001",
    cliente_id: str = CLIENTE_A,
    timestamp: str = "2026-05-07T10:00:00Z",
    tipo_decision: str = "INFORMAR",
    mensaje_original: str = "El margen está por debajo del umbral.",
    propuesta: dict | None = None,
    accion: str = "Notificar al dueño",
    overrides: dict | None = None,
    job_id: str | None = None,
) -> DecisionRecord:
    return DecisionRecord(
        decision_id=decision_id,
        cliente_id=cliente_id,
        timestamp=timestamp,
        tipo_decision=tipo_decision,
        mensaje_original=mensaje_original,
        propuesta=propuesta or {"umbral": 0.3, "margen_actual": 0.18},
        accion=accion,
        overrides=overrides,
        job_id=job_id,
    )


@pytest.fixture
def fake_client() -> FakeSupabaseClient:
    return FakeSupabaseClient()


@pytest.fixture
def repo(fake_client: FakeSupabaseClient) -> SupabaseDecisionsRepository:
    return SupabaseDecisionsRepository(cliente_id=CLIENTE_A, supabase_client=fake_client)


# ---------------------------------------------------------------------------
# cliente_id vacío falla cerrado
# ---------------------------------------------------------------------------

def test_cliente_id_vacio_lanza_error(fake_client):
    with pytest.raises(ValueError, match="cliente_id"):
        SupabaseDecisionsRepository(cliente_id="", supabase_client=fake_client)


def test_cliente_id_solo_espacios_lanza_error(fake_client):
    with pytest.raises(ValueError, match="cliente_id"):
        SupabaseDecisionsRepository(cliente_id="   ", supabase_client=fake_client)


# ---------------------------------------------------------------------------
# env incompleta falla solo cuando no se inyecta cliente
# ---------------------------------------------------------------------------

def test_sin_cliente_inyectado_y_sin_env_falla_cerrado(monkeypatch):
    """Sin cliente inyectado y sin env Supabase → BLOCKED_ENVIRONMENT_CONTRACT_MISSING."""
    monkeypatch.delenv("SMARTPYME_SUPABASE_URL", raising=False)
    monkeypatch.delenv("SMARTPYME_SUPABASE_KEY", raising=False)
    with pytest.raises(ValueError, match="BLOCKED_ENVIRONMENT_CONTRACT_MISSING"):
        SupabaseDecisionsRepository(cliente_id=CLIENTE_A)


def test_con_cliente_inyectado_no_requiere_env(monkeypatch, fake_client):
    """Con cliente inyectado, no se valida el entorno Supabase."""
    monkeypatch.delenv("SMARTPYME_SUPABASE_URL", raising=False)
    monkeypatch.delenv("SMARTPYME_SUPABASE_KEY", raising=False)
    repo = SupabaseDecisionsRepository(cliente_id=CLIENTE_A, supabase_client=fake_client)
    assert repo.cliente_id == CLIENTE_A


# ---------------------------------------------------------------------------
# create — inserta con cliente_id correcto
# ---------------------------------------------------------------------------

def test_create_inserta_fila(repo, fake_client):
    decision = _make_decision()
    repo.create(decision)
    rows = fake_client.get_rows("decisions")
    assert len(rows) == 1
    assert rows[0]["decision_id"] == "dec-001"
    assert rows[0]["cliente_id"] == CLIENTE_A


def test_create_conserva_decision_id(repo, fake_client):
    decision = _make_decision(decision_id="dec-xyz")
    repo.create(decision)
    rows = fake_client.get_rows("decisions")
    assert rows[0]["decision_id"] == "dec-xyz"


def test_create_conserva_decision_type(repo, fake_client):
    decision = _make_decision(tipo_decision="EJECUTAR")
    repo.create(decision)
    rows = fake_client.get_rows("decisions")
    assert rows[0]["decision_type"] == "EJECUTAR"


def test_create_conserva_decision_value(repo, fake_client):
    decision = _make_decision(accion="Aplicar descuento del 10%")
    repo.create(decision)
    rows = fake_client.get_rows("decisions")
    assert rows[0]["decision_value"] == "Aplicar descuento del 10%"


def test_create_conserva_case_id_desde_overrides(repo, fake_client):
    """case_id se extrae de overrides y se almacena en columna case_id."""
    decision = _make_decision(overrides={"case_id": "case-001"})
    repo.create(decision)
    rows = fake_client.get_rows("decisions")
    assert rows[0]["case_id"] == "case-001"


def test_create_conserva_report_id_desde_overrides(repo, fake_client):
    """report_id se extrae de overrides y se almacena en columna report_id."""
    decision = _make_decision(overrides={"report_id": "report-001"})
    repo.create(decision)
    rows = fake_client.get_rows("decisions")
    assert rows[0]["report_id"] == "report-001"


def test_create_rationale_es_dict_no_string(repo, fake_client):
    """rationale se inserta como dict, no como string."""
    decision = _make_decision(propuesta={"umbral": 0.3, "margen_actual": 0.18})
    repo.create(decision)
    rows = fake_client.get_rows("decisions")
    assert isinstance(rows[0]["rationale"], dict)
    assert rows[0]["rationale"]["umbral"] == 0.3


def test_create_metadata_es_dict(repo, fake_client):
    """metadata se inserta como dict."""
    decision = _make_decision()
    repo.create(decision)
    rows = fake_client.get_rows("decisions")
    assert isinstance(rows[0]["metadata"], dict)


def test_create_metadata_conserva_timestamp(repo, fake_client):
    decision = _make_decision(timestamp="2026-05-07T12:00:00Z")
    repo.create(decision)
    rows = fake_client.get_rows("decisions")
    assert rows[0]["metadata"]["timestamp"] == "2026-05-07T12:00:00Z"


def test_create_metadata_conserva_mensaje_original(repo, fake_client):
    decision = _make_decision(mensaje_original="Stock crítico detectado.")
    repo.create(decision)
    rows = fake_client.get_rows("decisions")
    assert rows[0]["metadata"]["mensaje_original"] == "Stock crítico detectado."


def test_create_metadata_conserva_job_id(repo, fake_client):
    decision = _make_decision(job_id="job-555")
    repo.create(decision)
    rows = fake_client.get_rows("decisions")
    assert rows[0]["metadata"]["job_id"] == "job-555"


def test_create_mismatch_cliente_id_falla_cerrado(repo):
    """create() rechaza decisión con cliente_id diferente al del repo."""
    decision = _make_decision(cliente_id=CLIENTE_B)
    with pytest.raises(ValueError, match="cliente_id mismatch"):
        repo.create(decision)


def test_create_no_inserta_en_mismatch(repo, fake_client):
    """Tras mismatch, la tabla queda vacía."""
    decision = _make_decision(cliente_id=CLIENTE_B)
    with pytest.raises(ValueError):
        repo.create(decision)
    assert fake_client.get_rows("decisions") == []


# ---------------------------------------------------------------------------
# get — filtra por cliente_id y decision_id
# ---------------------------------------------------------------------------

def test_get_retorna_decision_existente(repo):
    decision = _make_decision()
    repo.create(decision)
    fetched = repo.get("dec-001")
    assert fetched is not None
    assert fetched.decision_id == "dec-001"
    assert fetched.cliente_id == CLIENTE_A


def test_get_retorna_none_si_no_existe(repo):
    fetched = repo.get("dec-inexistente")
    assert fetched is None


def test_get_no_retorna_decision_de_otro_cliente(fake_client):
    """get() no retorna decisiones de otro cliente aunque compartan decision_id."""
    repo_a = SupabaseDecisionsRepository(cliente_id=CLIENTE_A, supabase_client=fake_client)
    repo_b = SupabaseDecisionsRepository(cliente_id=CLIENTE_B, supabase_client=fake_client)

    decision_a = _make_decision(decision_id="dec-shared", cliente_id=CLIENTE_A)
    repo_a.create(decision_a)

    assert repo_b.get("dec-shared") is None


def test_get_preserva_tipo_decision(repo):
    decision = _make_decision(tipo_decision="RECHAZAR")
    repo.create(decision)
    fetched = repo.get("dec-001")
    assert fetched.tipo_decision == "RECHAZAR"


def test_get_preserva_accion(repo):
    decision = _make_decision(accion="Bloquear pedido")
    repo.create(decision)
    fetched = repo.get("dec-001")
    assert fetched.accion == "Bloquear pedido"


def test_get_preserva_propuesta_como_dict(repo):
    propuesta = {"umbral": 0.25, "margen_actual": 0.10, "diferencia": 0.15}
    decision = _make_decision(propuesta=propuesta)
    repo.create(decision)
    fetched = repo.get("dec-001")
    assert isinstance(fetched.propuesta, dict)
    assert fetched.propuesta == propuesta


def test_get_preserva_case_id_en_overrides(repo):
    decision = _make_decision(overrides={"case_id": "case-abc"})
    repo.create(decision)
    fetched = repo.get("dec-001")
    assert fetched.overrides is not None
    assert fetched.overrides.get("case_id") == "case-abc"


def test_get_preserva_report_id_en_overrides(repo):
    decision = _make_decision(overrides={"report_id": "report-abc"})
    repo.create(decision)
    fetched = repo.get("dec-001")
    assert fetched.overrides is not None
    assert fetched.overrides.get("report_id") == "report-abc"


def test_get_preserva_job_id(repo):
    decision = _make_decision(job_id="job-777")
    repo.create(decision)
    fetched = repo.get("dec-001")
    assert fetched.job_id == "job-777"


# ---------------------------------------------------------------------------
# list_decisions — filtra por cliente_id
# ---------------------------------------------------------------------------

def test_list_decisions_retorna_decisiones_del_cliente(repo):
    repo.create(_make_decision(decision_id="dec-001"))
    repo.create(_make_decision(decision_id="dec-002"))
    decisions = repo.list_decisions()
    assert len(decisions) == 2
    assert all(d.cliente_id == CLIENTE_A for d in decisions)


def test_list_decisions_vacio_si_no_hay_decisiones(repo):
    assert repo.list_decisions() == []


def test_list_decisions_aislamiento_multi_cliente(fake_client):
    """list_decisions() nunca retorna decisiones de otro cliente."""
    repo_a = SupabaseDecisionsRepository(cliente_id=CLIENTE_A, supabase_client=fake_client)
    repo_b = SupabaseDecisionsRepository(cliente_id=CLIENTE_B, supabase_client=fake_client)

    repo_a.create(_make_decision(decision_id="dec-A1", cliente_id=CLIENTE_A))
    repo_a.create(_make_decision(decision_id="dec-A2", cliente_id=CLIENTE_A))
    repo_b.create(_make_decision(decision_id="dec-B1", cliente_id=CLIENTE_B))

    decisions_a = repo_a.list_decisions()
    decisions_b = repo_b.list_decisions()

    assert len(decisions_a) == 2
    assert all(d.cliente_id == CLIENTE_A for d in decisions_a)

    assert len(decisions_b) == 1
    assert decisions_b[0].decision_id == "dec-B1"
    assert decisions_b[0].cliente_id == CLIENTE_B


# ---------------------------------------------------------------------------
# DecisionPort protocol compliance
# ---------------------------------------------------------------------------

def test_supabase_decisions_repository_satisface_decision_port(fake_client):
    """SupabaseDecisionsRepository satisface el protocolo DecisionPort."""
    from app.repositories.persistence_ports import DecisionPort

    repo = SupabaseDecisionsRepository(cliente_id=CLIENTE_A, supabase_client=fake_client)
    assert isinstance(repo, DecisionPort)


# ---------------------------------------------------------------------------
# Sin llamadas de red en ningún test
# ---------------------------------------------------------------------------

def test_no_hay_llamadas_de_red(repo):
    """FakeSupabaseClient no hace llamadas de red — verificar que el repo usa el fake."""
    decision = _make_decision()
    repo.create(decision)
    fetched = repo.get("dec-001")
    assert fetched is not None
