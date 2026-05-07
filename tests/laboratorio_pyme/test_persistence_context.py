"""Tests de integración mínima Laboratorio MVP <-> repository_factory."""
from __future__ import annotations

from dataclasses import dataclass

import pytest

from app.contracts.decision_record import DecisionRecord
from app.contracts.diagnostic_report import DiagnosticReport
from app.contracts.evidence_contract import EvidenceChunk
from app.contracts.job_contract import Job, JobStatus
from app.contracts.operational_case import OperationalCase
from app.laboratorio_pyme.persistence import LaboratorioPersistenceContext
from app.laboratorio_pyme.service import LaboratorioService
from app.laboratorio_pyme.tipos import TipoLaboratorio


class _FakeResult:
    def __init__(self, data: list[dict]) -> None:
        self.data = data


class _FakeQueryBuilder:
    def __init__(self, store: list[dict]) -> None:
        self._store = store
        self._filters: list[tuple[str, object]] = []
        self._mode = "select"
        self._insert_row: dict | None = None

    def select(self, cols: str = "*") -> "_FakeQueryBuilder":
        self._mode = "select"
        return self

    def insert(self, row: dict) -> "_FakeQueryBuilder":
        self._mode = "insert"
        self._insert_row = row
        return self

    def eq(self, col: str, val: object) -> "_FakeQueryBuilder":
        self._filters.append((col, val))
        return self

    def execute(self) -> _FakeResult:
        if self._mode == "insert":
            self._store.append(dict(self._insert_row or {}))
            return _FakeResult([])
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


@dataclass
class _FakeContext:
    jobs: object


def test_laboratorio_service_funciona_con_contexto_inyectado_fake() -> None:
    svc = LaboratorioService(persistence_context=_FakeContext(jobs=object()))
    caso = svc.crear_caso(
        "cliente-A",
        "Ana",
        [TipoLaboratorio.analisis_comercial],
        job_id="job-1",
    )
    assert caso.cliente_id == "cliente-A"
    assert svc.persistence_context is not None


def test_context_resuelve_repos_supabase_desde_factory_con_fake_client() -> None:
    fake = FakeSupabaseClient()
    ctx = LaboratorioPersistenceContext.from_repository_factory(
        cliente_id="cliente-A",
        provider="supabase",
        supabase_client=fake,
    )
    assert ctx.jobs._client is fake
    assert ctx.operational_cases._client is fake
    assert ctx.reports._client is fake
    assert ctx.decisions._client is fake
    assert ctx.evidence_candidates._client is fake
    assert ctx.clientes._client is fake


def test_context_supabase_preserva_cliente_id_en_flujo_core() -> None:
    fake = FakeSupabaseClient()
    cliente_id = "cliente-A"
    ctx = LaboratorioPersistenceContext.from_repository_factory(
        cliente_id=cliente_id,
        provider="supabase",
        supabase_client=fake,
    )

    job = Job(
        job_id="job-1",
        cliente_id=cliente_id,
        job_type="LABORATORIO_MVP",
        status=JobStatus.PENDING,
    )
    ctx.jobs.create(job)
    assert ctx.jobs.get("job-1").cliente_id == cliente_id

    op_case = OperationalCase(
        cliente_id=cliente_id,
        case_id="case-1",
        job_id="job-1",
        skill_id="laboratorio_pyme",
        hypothesis="Investigar si hay caida de ventas?",
        evidence_ids=["ev-1"],
        status="OPEN",
    )
    ctx.operational_cases.create_case(op_case)
    assert ctx.operational_cases.get_case("case-1").cliente_id == cliente_id

    report = DiagnosticReport(
        cliente_id=cliente_id,
        report_id="rep-1",
        case_id="case-1",
        hypothesis="Investigar si hay caida de ventas?",
        diagnosis_status="CONFIRMED",
        findings=[{"hallazgo": "caida"}],
        evidence_used=["ev-1"],
        reasoning_summary="Evidencia consistente",
    )
    ctx.reports.create_report(report)
    assert ctx.reports.get_report("rep-1").cliente_id == cliente_id

    decision = DecisionRecord(
        decision_id="dec-1",
        cliente_id=cliente_id,
        timestamp="2026-05-07T00:00:00Z",
        tipo_decision="INFORMAR",
        mensaje_original="mensaje",
        propuesta={"accion": "informar"},
        accion="informar_cliente",
        overrides={"case_id": "case-1", "report_id": "rep-1"},
        job_id="job-1",
    )
    ctx.decisions.create(decision)
    assert ctx.decisions.get("dec-1").cliente_id == cliente_id

    evidence = EvidenceChunk(
        cliente_id=cliente_id,
        evidence_id="ev-1",
        document_id="doc-1",
        raw_document_id="raw-1",
        job_id="job-1",
        plan_id="plan-1",
        filename="ventas.csv",
        page=1,
        text="texto",
        chunk_order=0,
        metadata={"source": "test"},
    )
    ctx.evidence_candidates.create(evidence)
    assert ctx.evidence_candidates.get("ev-1").cliente_id == cliente_id

    fake.table("clientes").insert({"cliente_id": cliente_id, "status": "active"}).execute()
    assert ctx.clientes.exists(cliente_id) is True


def test_context_provider_por_env_supabase_con_fake_client(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SMARTPYME_PERSISTENCE_PROVIDER", "supabase")
    ctx = LaboratorioPersistenceContext.from_repository_factory(
        cliente_id="cliente-A",
        supabase_client=FakeSupabaseClient(),
    )
    assert ctx.jobs is not None


def test_context_sqlite_falla_cerrado_para_entidades_no_disponibles(tmp_path) -> None:
    with pytest.raises(NotImplementedError, match="SQLITE_REPOSITORY_NOT_AVAILABLE_FOR_P0_ENTITY"):
        LaboratorioPersistenceContext.from_repository_factory(
            cliente_id="cliente-A",
            provider="sqlite",
            db_path=tmp_path / "db.sqlite",
        )

