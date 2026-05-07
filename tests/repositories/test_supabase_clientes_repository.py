"""Tests del adapter Supabase para clientes — SmartPyme P0.

Usa FakeSupabaseClient (in-memory, sin red) para probar:
- get devuelve cliente por cliente_id.
- get devuelve None si no existe.
- get no acepta cliente_id vacío.
- exists devuelve True si existe.
- exists devuelve False si no existe.
- exists no acepta cliente_id vacío.
- usa tabla clientes.
- env incompleta falla solo cuando no se inyecta cliente.
- tests no hacen network call.
- no regresan tests previos.
- protocol compliance con ClientePort.
"""
import pytest

from app.repositories.supabase_clientes_repository import SupabaseClientesRepository


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

    def seed_cliente(self, row: dict) -> None:
        """Helper de test para insertar un cliente directamente en el store."""
        if "clientes" not in self._tables:
            self._tables["clientes"] = []
        self._tables["clientes"].append(dict(row))

    def get_rows(self, table: str) -> list[dict]:
        """Helper de test para inspeccionar el estado interno."""
        return list(self._tables.get(table, []))


# ---------------------------------------------------------------------------
# Fixtures y helpers
# ---------------------------------------------------------------------------

CLIENTE_A = "cliente-A"
CLIENTE_B = "cliente-B"


def _make_cliente_row(
    cliente_id: str = CLIENTE_A,
    nombre: str = "Empresa Ejemplo S.A.",
    status: str = "active",
    metadata: dict | None = None,
    created_at: str = "2026-01-01T00:00:00Z",
    updated_at: str = "2026-05-07T00:00:00Z",
) -> dict:
    return {
        "cliente_id": cliente_id,
        "nombre": nombre,
        "status": status,
        "metadata": metadata or {},
        "created_at": created_at,
        "updated_at": updated_at,
    }


@pytest.fixture
def fake_client() -> FakeSupabaseClient:
    return FakeSupabaseClient()


@pytest.fixture
def repo(fake_client: FakeSupabaseClient) -> SupabaseClientesRepository:
    return SupabaseClientesRepository(supabase_client=fake_client)


@pytest.fixture
def repo_con_cliente(fake_client: FakeSupabaseClient) -> SupabaseClientesRepository:
    """Repo con un cliente pre-cargado en el store."""
    fake_client.seed_cliente(_make_cliente_row())
    return SupabaseClientesRepository(supabase_client=fake_client)


# ---------------------------------------------------------------------------
# env incompleta falla solo cuando no se inyecta cliente
# ---------------------------------------------------------------------------

def test_sin_cliente_inyectado_y_sin_env_falla_cerrado(monkeypatch):
    """Sin cliente inyectado y sin env Supabase → BLOCKED_ENVIRONMENT_CONTRACT_MISSING."""
    monkeypatch.delenv("SMARTPYME_SUPABASE_URL", raising=False)
    monkeypatch.delenv("SMARTPYME_SUPABASE_KEY", raising=False)
    with pytest.raises(ValueError, match="BLOCKED_ENVIRONMENT_CONTRACT_MISSING"):
        SupabaseClientesRepository()


def test_con_cliente_inyectado_no_requiere_env(monkeypatch, fake_client):
    """Con cliente inyectado, no se valida el entorno Supabase."""
    monkeypatch.delenv("SMARTPYME_SUPABASE_URL", raising=False)
    monkeypatch.delenv("SMARTPYME_SUPABASE_KEY", raising=False)
    # No debe lanzar
    repo = SupabaseClientesRepository(supabase_client=fake_client)
    assert repo is not None


# ---------------------------------------------------------------------------
# get — devuelve cliente por cliente_id
# ---------------------------------------------------------------------------

def test_get_devuelve_cliente_existente(repo_con_cliente):
    result = repo_con_cliente.get(CLIENTE_A)
    assert result is not None
    assert result["cliente_id"] == CLIENTE_A


def test_get_devuelve_none_si_no_existe(repo):
    result = repo.get("cliente-inexistente")
    assert result is None


def test_get_devuelve_dict_normalizado(repo_con_cliente):
    """get() devuelve dict con claves canónicas P0."""
    result = repo_con_cliente.get(CLIENTE_A)
    assert "cliente_id" in result
    assert "nombre" in result
    assert "status" in result
    assert "metadata" in result
    assert "created_at" in result
    assert "updated_at" in result


def test_get_preserva_nombre(fake_client):
    fake_client.seed_cliente(_make_cliente_row(nombre="Distribuidora Norte"))
    repo = SupabaseClientesRepository(supabase_client=fake_client)
    result = repo.get(CLIENTE_A)
    assert result["nombre"] == "Distribuidora Norte"


def test_get_preserva_status(fake_client):
    fake_client.seed_cliente(_make_cliente_row(status="inactive"))
    repo = SupabaseClientesRepository(supabase_client=fake_client)
    result = repo.get(CLIENTE_A)
    assert result["status"] == "inactive"


def test_get_preserva_metadata(fake_client):
    fake_client.seed_cliente(_make_cliente_row(metadata={"plan": "pro", "region": "AR"}))
    repo = SupabaseClientesRepository(supabase_client=fake_client)
    result = repo.get(CLIENTE_A)
    assert result["metadata"]["plan"] == "pro"
    assert result["metadata"]["region"] == "AR"


def test_get_no_retorna_otro_cliente(fake_client):
    """get() no retorna datos de otro cliente_id."""
    fake_client.seed_cliente(_make_cliente_row(cliente_id=CLIENTE_A))
    fake_client.seed_cliente(_make_cliente_row(cliente_id=CLIENTE_B, nombre="Otro"))
    repo = SupabaseClientesRepository(supabase_client=fake_client)
    result = repo.get(CLIENTE_A)
    assert result["cliente_id"] == CLIENTE_A
    assert result["nombre"] != "Otro"


# ---------------------------------------------------------------------------
# get — falla cerrado con cliente_id vacío
# ---------------------------------------------------------------------------

def test_get_cliente_id_vacio_lanza_error(repo):
    with pytest.raises(ValueError, match="cliente_id"):
        repo.get("")


def test_get_cliente_id_solo_espacios_lanza_error(repo):
    with pytest.raises(ValueError, match="cliente_id"):
        repo.get("   ")


# ---------------------------------------------------------------------------
# exists — devuelve True/False
# ---------------------------------------------------------------------------

def test_exists_retorna_true_si_existe(repo_con_cliente):
    assert repo_con_cliente.exists(CLIENTE_A) is True


def test_exists_retorna_false_si_no_existe(repo):
    assert repo.exists("cliente-inexistente") is False


def test_exists_distingue_clientes(fake_client):
    """exists() distingue entre clientes distintos."""
    fake_client.seed_cliente(_make_cliente_row(cliente_id=CLIENTE_A))
    repo = SupabaseClientesRepository(supabase_client=fake_client)
    assert repo.exists(CLIENTE_A) is True
    assert repo.exists(CLIENTE_B) is False


# ---------------------------------------------------------------------------
# exists — falla cerrado con cliente_id vacío
# ---------------------------------------------------------------------------

def test_exists_cliente_id_vacio_lanza_error(repo):
    with pytest.raises(ValueError, match="cliente_id"):
        repo.exists("")


def test_exists_cliente_id_solo_espacios_lanza_error(repo):
    with pytest.raises(ValueError, match="cliente_id"):
        repo.exists("   ")


# ---------------------------------------------------------------------------
# Usa tabla clientes
# ---------------------------------------------------------------------------

def test_usa_tabla_clientes(fake_client):
    """El adapter opera sobre la tabla 'clientes'."""
    fake_client.seed_cliente(_make_cliente_row())
    repo = SupabaseClientesRepository(supabase_client=fake_client)
    # Si usara otra tabla, get() devolvería None.
    result = repo.get(CLIENTE_A)
    assert result is not None
    # Confirmar que la tabla 'clientes' tiene la fila.
    assert len(fake_client.get_rows("clientes")) == 1


# ---------------------------------------------------------------------------
# ClientePort protocol compliance
# ---------------------------------------------------------------------------

def test_supabase_clientes_repository_satisface_cliente_port(fake_client):
    """SupabaseClientesRepository satisface el protocolo ClientePort."""
    from app.repositories.persistence_ports import ClientePort

    repo = SupabaseClientesRepository(supabase_client=fake_client)
    assert isinstance(repo, ClientePort)


# ---------------------------------------------------------------------------
# Sin llamadas de red en ningún test
# ---------------------------------------------------------------------------

def test_no_hay_llamadas_de_red(fake_client):
    """FakeSupabaseClient no hace llamadas de red — verificar que el repo usa el fake."""
    fake_client.seed_cliente(_make_cliente_row())
    repo = SupabaseClientesRepository(supabase_client=fake_client)
    result = repo.get(CLIENTE_A)
    assert result is not None
