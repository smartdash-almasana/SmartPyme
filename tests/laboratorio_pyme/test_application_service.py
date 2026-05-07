"""Tests del LaboratorioApplicationService — SmartPyme P0.

Cubre:
- crea caso persistente con fake repos.
- persiste job y operational_case en fake repos.
- conserva cliente_id.
- no llama red.
- falla cerrado si falta persistence_context.
- no persiste LaboratorioReportDraft como entidad propia.
- no rompe tests existentes.
"""
from __future__ import annotations

import pytest

from app.contracts.job_contract import JobStatus
from app.laboratorio_pyme.application_service import (
    CasoPersistenteResult,
    LaboratorioApplicationService,
)
from app.laboratorio_pyme.persistence import LaboratorioPersistenceContext
from app.laboratorio_pyme.service import LaboratorioService
from app.laboratorio_pyme.tipos import TipoLaboratorio


# ---------------------------------------------------------------------------
# FakeSupabaseClient — in-memory sin red
# ---------------------------------------------------------------------------

class _FakeResult:
    def __init__(self, data: list[dict]) -> None:
        self.data = data


class _FakeQueryBuilder:
    def __init__(self, store: list[dict]) -> None:
        self._store = store
        self._filters: list[tuple[str, object]] = []
        self._mode = "select"
        self._insert_row: dict | None = None
        self._update_patch: dict | None = None

    def select(self, cols: str = "*") -> "_FakeQueryBuilder":
        self._mode = "select"
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

    def execute(self) -> _FakeResult:
        if self._mode == "insert":
            self._store.append(dict(self._insert_row or {}))
            return _FakeResult([])
        if self._mode == "update":
            updated = []
            for row in self._store:
                if all(row.get(c) == v for c, v in self._filters):
                    row.update(self._update_patch or {})
                    updated.append(dict(row))
            return _FakeResult(updated)
        result = list(self._store)
        for col, val in self._filters:
            result = [r for r in result if r.get(col) == val]
        return _FakeResult(result)


class FakeSupabaseClient:
    def __init__(self) -> None:
        self._tables: dict[str, list[dict]] = {}

    def table(self, name: str) -> _FakeQueryBuilder:
        if name not in self._tables:
            self._tables[name] = []
        return _FakeQueryBuilder(self._tables[name])

    def get_rows(self, table: str) -> list[dict]:
        return list(self._tables.get(table, []))


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

CLIENTE_A = "cliente-A"


@pytest.fixture
def fake_client() -> FakeSupabaseClient:
    return FakeSupabaseClient()


@pytest.fixture
def ctx(fake_client: FakeSupabaseClient) -> LaboratorioPersistenceContext:
    return LaboratorioPersistenceContext.from_repository_factory(
        cliente_id=CLIENTE_A,
        provider="supabase",
        supabase_client=fake_client,
    )


@pytest.fixture
def svc() -> LaboratorioService:
    return LaboratorioService()


@pytest.fixture
def app_svc(svc: LaboratorioService, ctx: LaboratorioPersistenceContext) -> LaboratorioApplicationService:
    return LaboratorioApplicationService(
        laboratorio_service=svc,
        persistence_context=ctx,
    )


# ---------------------------------------------------------------------------
# falla cerrado si falta persistence_context
# ---------------------------------------------------------------------------

def test_falla_cerrado_si_persistence_context_es_none(svc):
    with pytest.raises(ValueError, match="persistence_context"):
        LaboratorioApplicationService(
            laboratorio_service=svc,
            persistence_context=None,
        )


# ---------------------------------------------------------------------------
# crear_caso_persistente — flujo básico
# ---------------------------------------------------------------------------

def test_crear_caso_persistente_devuelve_result(app_svc):
    result = app_svc.crear_caso_persistente(
        cliente_id=CLIENTE_A,
        dueno_nombre="Ana García",
        laboratorios=[TipoLaboratorio.analisis_comercial],
    )
    assert isinstance(result, CasoPersistenteResult)


def test_crear_caso_persistente_conserva_cliente_id(app_svc):
    result = app_svc.crear_caso_persistente(
        cliente_id=CLIENTE_A,
        dueno_nombre="Ana García",
        laboratorios=[TipoLaboratorio.analisis_comercial],
    )
    assert result.cliente_id == CLIENTE_A


def test_crear_caso_persistente_devuelve_case_id_no_vacio(app_svc):
    result = app_svc.crear_caso_persistente(
        cliente_id=CLIENTE_A,
        dueno_nombre="Ana García",
        laboratorios=[TipoLaboratorio.analisis_comercial],
    )
    assert result.case_id
    assert len(result.case_id) > 0


def test_crear_caso_persistente_devuelve_job_id_no_vacio(app_svc):
    result = app_svc.crear_caso_persistente(
        cliente_id=CLIENTE_A,
        dueno_nombre="Ana García",
        laboratorios=[TipoLaboratorio.analisis_comercial],
    )
    assert result.job_id
    assert len(result.job_id) > 0


def test_crear_caso_persistente_preserva_job_id_provisto(app_svc):
    """Si se provee job_id, se usa ese y no se genera uno nuevo."""
    result = app_svc.crear_caso_persistente(
        cliente_id=CLIENTE_A,
        dueno_nombre="Ana García",
        laboratorios=[TipoLaboratorio.analisis_comercial],
        job_id="job-externo-001",
    )
    assert result.job_id == "job-externo-001"


def test_crear_caso_persistente_laboratorio_case_tiene_cliente_id(app_svc):
    result = app_svc.crear_caso_persistente(
        cliente_id=CLIENTE_A,
        dueno_nombre="Ana García",
        laboratorios=[TipoLaboratorio.analisis_financiero],
    )
    assert result.laboratorio_case.cliente_id == CLIENTE_A


def test_crear_caso_persistente_laboratorio_case_tiene_laboratorios(app_svc):
    result = app_svc.crear_caso_persistente(
        cliente_id=CLIENTE_A,
        dueno_nombre="Ana García",
        laboratorios=[TipoLaboratorio.analisis_stock, TipoLaboratorio.analisis_compras],
    )
    assert TipoLaboratorio.analisis_stock in result.laboratorio_case.laboratorios
    assert TipoLaboratorio.analisis_compras in result.laboratorio_case.laboratorios


# ---------------------------------------------------------------------------
# persiste Job en fake repo
# ---------------------------------------------------------------------------

def test_persiste_job_en_repo(app_svc, fake_client):
    result = app_svc.crear_caso_persistente(
        cliente_id=CLIENTE_A,
        dueno_nombre="Ana García",
        laboratorios=[TipoLaboratorio.analisis_comercial],
    )
    rows = fake_client.get_rows("jobs")
    assert len(rows) == 1
    assert rows[0]["job_id"] == result.job_id
    assert rows[0]["cliente_id"] == CLIENTE_A


def test_job_persistido_tiene_tipo_laboratorio_mvp(app_svc, fake_client):
    app_svc.crear_caso_persistente(
        cliente_id=CLIENTE_A,
        dueno_nombre="Ana García",
        laboratorios=[TipoLaboratorio.analisis_comercial],
    )
    rows = fake_client.get_rows("jobs")
    assert rows[0]["job_type"] == "LABORATORIO_MVP"


def test_job_persistido_tiene_status_pending(app_svc, fake_client):
    app_svc.crear_caso_persistente(
        cliente_id=CLIENTE_A,
        dueno_nombre="Ana García",
        laboratorios=[TipoLaboratorio.analisis_comercial],
    )
    rows = fake_client.get_rows("jobs")
    assert rows[0]["status"] == str(JobStatus.PENDING)


def test_job_persistido_payload_contiene_dueno_nombre(app_svc, fake_client):
    app_svc.crear_caso_persistente(
        cliente_id=CLIENTE_A,
        dueno_nombre="Carlos López",
        laboratorios=[TipoLaboratorio.analisis_comercial],
    )
    rows = fake_client.get_rows("jobs")
    assert rows[0]["payload"]["dueno_nombre"] == "Carlos López"


# ---------------------------------------------------------------------------
# persiste OperationalCase en fake repo
# ---------------------------------------------------------------------------

def test_persiste_operational_case_en_repo(app_svc, fake_client):
    result = app_svc.crear_caso_persistente(
        cliente_id=CLIENTE_A,
        dueno_nombre="Ana García",
        laboratorios=[TipoLaboratorio.analisis_comercial],
    )
    rows = fake_client.get_rows("operational_cases")
    assert len(rows) == 1
    assert rows[0]["case_id"] == result.case_id
    assert rows[0]["cliente_id"] == CLIENTE_A


def test_operational_case_persistido_tiene_job_id(app_svc, fake_client):
    result = app_svc.crear_caso_persistente(
        cliente_id=CLIENTE_A,
        dueno_nombre="Ana García",
        laboratorios=[TipoLaboratorio.analisis_comercial],
    )
    rows = fake_client.get_rows("operational_cases")
    assert rows[0]["job_id"] == result.job_id


def test_operational_case_persistido_tiene_status_open(app_svc, fake_client):
    app_svc.crear_caso_persistente(
        cliente_id=CLIENTE_A,
        dueno_nombre="Ana García",
        laboratorios=[TipoLaboratorio.analisis_comercial],
    )
    rows = fake_client.get_rows("operational_cases")
    assert rows[0]["status"] == "OPEN"


def test_case_id_y_job_id_son_consistentes(app_svc, fake_client):
    """El case_id del OperationalCase coincide con el del LaboratorioPymeCase."""
    result = app_svc.crear_caso_persistente(
        cliente_id=CLIENTE_A,
        dueno_nombre="Ana García",
        laboratorios=[TipoLaboratorio.analisis_comercial],
    )
    case_rows = fake_client.get_rows("operational_cases")
    job_rows = fake_client.get_rows("jobs")
    assert case_rows[0]["case_id"] == result.case_id
    assert job_rows[0]["job_id"] == result.job_id
    assert case_rows[0]["job_id"] == job_rows[0]["job_id"]


# ---------------------------------------------------------------------------
# LaboratorioReportDraft NO se persiste
# ---------------------------------------------------------------------------

def test_no_persiste_laboratorio_report_draft(app_svc, fake_client):
    """crear_caso_persistente no persiste LaboratorioReportDraft."""
    app_svc.crear_caso_persistente(
        cliente_id=CLIENTE_A,
        dueno_nombre="Ana García",
        laboratorios=[TipoLaboratorio.analisis_comercial],
    )
    # Solo jobs y operational_cases deben tener filas.
    assert len(fake_client.get_rows("jobs")) == 1
    assert len(fake_client.get_rows("operational_cases")) == 1
    # reports, decisions, evidence_candidates deben estar vacíos.
    assert fake_client.get_rows("reports") == []
    assert fake_client.get_rows("decisions") == []
    assert fake_client.get_rows("evidence_candidates") == []


# ---------------------------------------------------------------------------
# Sin llamadas de red
# ---------------------------------------------------------------------------

def test_no_hay_llamadas_de_red(app_svc):
    """FakeSupabaseClient no hace llamadas de red."""
    result = app_svc.crear_caso_persistente(
        cliente_id=CLIENTE_A,
        dueno_nombre="Ana García",
        laboratorios=[TipoLaboratorio.analisis_comercial],
    )
    assert result is not None
