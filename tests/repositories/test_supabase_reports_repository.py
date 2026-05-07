"""Tests del adapter Supabase para reports — SmartPyme P0.

Usa FakeSupabaseClient (in-memory, sin red) para probar:
- create_report inserta con cliente_id correcto.
- create_report conserva report_id, case_id, job_id, status, payload, result, metadata.
- get_report filtra por cliente_id y report_id.
- get_report no filtra cruzado entre clientes.
- cliente_id vacío falla cerrado.
- mismatch de cliente_id falla cerrado.
- env incompleta falla solo cuando no se inyecta cliente.
- tests no hacen network call.
- no regresan tests previos.
- protocol compliance con ReportPort.
"""
import pytest

from app.contracts.diagnostic_report import DiagnosticReport
from app.repositories.supabase_reports_repository import SupabaseReportsRepository


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


def _make_report(
    report_id: str = "report-001",
    cliente_id: str = CLIENTE_A,
    case_id: str = "case-001",
    hypothesis: str = "Investigar si el margen bruto está por debajo del umbral esperado",
    diagnosis_status: str = "CONFIRMED",
    findings: list[dict] | None = None,
    evidence_used: list[str] | None = None,
    reasoning_summary: str = "Análisis completado con evidencia suficiente.",
) -> DiagnosticReport:
    return DiagnosticReport(
        report_id=report_id,
        cliente_id=cliente_id,
        case_id=case_id,
        hypothesis=hypothesis,
        diagnosis_status=diagnosis_status,
        findings=findings or [{"hallazgo": "margen bajo", "impacto": "alto"}],
        evidence_used=evidence_used or ["ev-001", "ev-002"],
        reasoning_summary=reasoning_summary,
    )


@pytest.fixture
def fake_client() -> FakeSupabaseClient:
    return FakeSupabaseClient()


@pytest.fixture
def repo(fake_client: FakeSupabaseClient) -> SupabaseReportsRepository:
    return SupabaseReportsRepository(cliente_id=CLIENTE_A, supabase_client=fake_client)


# ---------------------------------------------------------------------------
# cliente_id vacío falla cerrado
# ---------------------------------------------------------------------------

def test_cliente_id_vacio_lanza_error(fake_client):
    with pytest.raises(ValueError, match="cliente_id"):
        SupabaseReportsRepository(cliente_id="", supabase_client=fake_client)


def test_cliente_id_solo_espacios_lanza_error(fake_client):
    with pytest.raises(ValueError, match="cliente_id"):
        SupabaseReportsRepository(cliente_id="   ", supabase_client=fake_client)


# ---------------------------------------------------------------------------
# env incompleta falla solo cuando no se inyecta cliente
# ---------------------------------------------------------------------------

def test_sin_cliente_inyectado_y_sin_env_falla_cerrado(monkeypatch):
    """Sin cliente inyectado y sin env Supabase → BLOCKED_ENVIRONMENT_CONTRACT_MISSING."""
    monkeypatch.delenv("SMARTPYME_SUPABASE_URL", raising=False)
    monkeypatch.delenv("SMARTPYME_SUPABASE_KEY", raising=False)
    with pytest.raises(ValueError, match="BLOCKED_ENVIRONMENT_CONTRACT_MISSING"):
        SupabaseReportsRepository(cliente_id=CLIENTE_A)


def test_con_cliente_inyectado_no_requiere_env(monkeypatch, fake_client):
    """Con cliente inyectado, no se valida el entorno Supabase."""
    monkeypatch.delenv("SMARTPYME_SUPABASE_URL", raising=False)
    monkeypatch.delenv("SMARTPYME_SUPABASE_KEY", raising=False)
    repo = SupabaseReportsRepository(cliente_id=CLIENTE_A, supabase_client=fake_client)
    assert repo.cliente_id == CLIENTE_A


# ---------------------------------------------------------------------------
# create_report — inserta con cliente_id correcto
# ---------------------------------------------------------------------------

def test_create_report_inserta_fila(repo, fake_client):
    report = _make_report()
    repo.create_report(report)
    rows = fake_client.get_rows("reports")
    assert len(rows) == 1
    assert rows[0]["report_id"] == "report-001"
    assert rows[0]["cliente_id"] == CLIENTE_A


def test_create_report_conserva_report_id(repo, fake_client):
    report = _make_report(report_id="report-xyz")
    repo.create_report(report)
    rows = fake_client.get_rows("reports")
    assert rows[0]["report_id"] == "report-xyz"


def test_create_report_conserva_case_id(repo, fake_client):
    report = _make_report(case_id="case-999")
    repo.create_report(report)
    rows = fake_client.get_rows("reports")
    assert rows[0]["case_id"] == "case-999"


def test_create_report_conserva_status(repo, fake_client):
    report = _make_report(diagnosis_status="NOT_CONFIRMED")
    repo.create_report(report)
    rows = fake_client.get_rows("reports")
    assert rows[0]["status"] == "NOT_CONFIRMED"


def test_create_report_payload_es_dict_no_string(repo, fake_client):
    """payload se inserta como dict, no como string."""
    report = _make_report()
    repo.create_report(report)
    rows = fake_client.get_rows("reports")
    assert isinstance(rows[0]["payload"], dict)


def test_create_report_payload_contiene_findings(repo, fake_client):
    findings = [{"hallazgo": "stock negativo", "impacto": "critico"}]
    report = _make_report(findings=findings)
    repo.create_report(report)
    rows = fake_client.get_rows("reports")
    assert rows[0]["payload"]["findings"] == findings


def test_create_report_payload_contiene_evidence_used(repo, fake_client):
    report = _make_report(evidence_used=["ev-A", "ev-B", "ev-C"])
    repo.create_report(report)
    rows = fake_client.get_rows("reports")
    assert rows[0]["payload"]["evidence_used"] == ["ev-A", "ev-B", "ev-C"]


def test_create_report_payload_contiene_reasoning_summary(repo, fake_client):
    report = _make_report(reasoning_summary="Evidencia insuficiente para confirmar.")
    repo.create_report(report)
    rows = fake_client.get_rows("reports")
    assert rows[0]["payload"]["reasoning_summary"] == "Evidencia insuficiente para confirmar."


def test_create_report_result_es_none_por_defecto(repo, fake_client):
    report = _make_report()
    repo.create_report(report)
    rows = fake_client.get_rows("reports")
    assert rows[0]["result"] is None


def test_create_report_metadata_es_dict(repo, fake_client):
    """metadata se inserta como dict."""
    report = _make_report()
    repo.create_report(report)
    rows = fake_client.get_rows("reports")
    assert isinstance(rows[0]["metadata"], dict)


def test_create_report_mismatch_cliente_id_falla_cerrado(repo):
    """create_report() rechaza reporte con cliente_id diferente al del repo."""
    report = _make_report(cliente_id=CLIENTE_B)
    with pytest.raises(ValueError, match="cliente_id mismatch"):
        repo.create_report(report)


def test_create_report_no_inserta_en_mismatch(repo, fake_client):
    """Tras mismatch, la tabla queda vacía."""
    report = _make_report(cliente_id=CLIENTE_B)
    with pytest.raises(ValueError):
        repo.create_report(report)
    assert fake_client.get_rows("reports") == []


# ---------------------------------------------------------------------------
# get_report — filtra por cliente_id y report_id
# ---------------------------------------------------------------------------

def test_get_report_retorna_reporte_existente(repo):
    report = _make_report()
    repo.create_report(report)
    fetched = repo.get_report("report-001")
    assert fetched is not None
    assert fetched.report_id == "report-001"
    assert fetched.cliente_id == CLIENTE_A


def test_get_report_retorna_none_si_no_existe(repo):
    fetched = repo.get_report("report-inexistente")
    assert fetched is None


def test_get_report_no_retorna_reporte_de_otro_cliente(fake_client):
    """get_report() no retorna reportes de otro cliente aunque compartan report_id."""
    repo_a = SupabaseReportsRepository(cliente_id=CLIENTE_A, supabase_client=fake_client)
    repo_b = SupabaseReportsRepository(cliente_id=CLIENTE_B, supabase_client=fake_client)

    report_a = _make_report(report_id="report-shared", cliente_id=CLIENTE_A)
    repo_a.create_report(report_a)

    assert repo_b.get_report("report-shared") is None


def test_get_report_preserva_case_id(repo):
    report = _make_report(case_id="case-abc")
    repo.create_report(report)
    fetched = repo.get_report("report-001")
    assert fetched.case_id == "case-abc"


def test_get_report_preserva_diagnosis_status(repo):
    report = _make_report(diagnosis_status="INSUFFICIENT_EVIDENCE")
    repo.create_report(report)
    fetched = repo.get_report("report-001")
    assert fetched.diagnosis_status == "INSUFFICIENT_EVIDENCE"


def test_get_report_preserva_findings(repo):
    findings = [{"hallazgo": "rotacion baja", "impacto": "medio"}]
    report = _make_report(findings=findings)
    repo.create_report(report)
    fetched = repo.get_report("report-001")
    assert fetched.findings == findings


def test_get_report_preserva_evidence_used(repo):
    report = _make_report(evidence_used=["ev-X", "ev-Y"])
    repo.create_report(report)
    fetched = repo.get_report("report-001")
    assert fetched.evidence_used == ["ev-X", "ev-Y"]


def test_get_report_preserva_reasoning_summary(repo):
    report = _make_report(reasoning_summary="Diagnóstico confirmado por tres fuentes.")
    repo.create_report(report)
    fetched = repo.get_report("report-001")
    assert fetched.reasoning_summary == "Diagnóstico confirmado por tres fuentes."


def test_get_report_preserva_hypothesis(repo):
    hypothesis = "Investigar si el stock de producto A está por debajo del mínimo?"
    report = _make_report(hypothesis=hypothesis)
    repo.create_report(report)
    fetched = repo.get_report("report-001")
    assert fetched.hypothesis == hypothesis


# ---------------------------------------------------------------------------
# ReportPort protocol compliance
# ---------------------------------------------------------------------------

def test_supabase_reports_repository_satisface_report_port(fake_client):
    """SupabaseReportsRepository satisface el protocolo ReportPort."""
    from app.repositories.persistence_ports import ReportPort

    repo = SupabaseReportsRepository(cliente_id=CLIENTE_A, supabase_client=fake_client)
    assert isinstance(repo, ReportPort)


# ---------------------------------------------------------------------------
# Sin llamadas de red en ningún test
# ---------------------------------------------------------------------------

def test_no_hay_llamadas_de_red(repo):
    """FakeSupabaseClient no hace llamadas de red — verificar que el repo usa el fake."""
    report = _make_report()
    repo.create_report(report)
    fetched = repo.get_report("report-001")
    assert fetched is not None
