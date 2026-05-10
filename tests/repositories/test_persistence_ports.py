"""Tests de los puertos de persistencia P0 de SmartPyme.

Verifica que:
- Los 6 puertos existen y son importables.
- Cada puerto es un Protocol con @runtime_checkable.
- Los métodos requeridos están definidos con las firmas correctas.
- Los docstrings codifican el requisito de cliente_id.
- Ningún puerto tiene métodos de persistencia directa de LaboratorioReportDraft.
- Los puertos son estructuralmente correctos para duck typing.
"""
import inspect

import pytest

from app.repositories.persistence_ports import (
    ClientePort,
    DecisionPort,
    EvidenceCandidatePort,
    JobPort,
    OperationalCasePort,
    ReportPort,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_method_names(port_class) -> set[str]:
    """Retorna los nombres de métodos públicos definidos en el Protocol."""
    return {
        name
        for name, member in inspect.getmembers(port_class, predicate=inspect.isfunction)
        if not name.startswith("_")
    }


def _get_docstring(port_class) -> str:
    return inspect.getdoc(port_class) or ""


def _get_method_docstring(port_class, method_name: str) -> str:
    method = getattr(port_class, method_name, None)
    if method is None:
        return ""
    return inspect.getdoc(method) or ""


# ---------------------------------------------------------------------------
# Existencia e importabilidad de los 6 puertos
# ---------------------------------------------------------------------------

def test_job_port_importable():
    assert JobPort is not None


def test_operational_case_port_importable():
    assert OperationalCasePort is not None


def test_report_port_importable():
    assert ReportPort is not None


def test_decision_port_importable():
    assert DecisionPort is not None


def test_evidence_candidate_port_importable():
    assert EvidenceCandidatePort is not None


def test_cliente_port_importable():
    assert ClientePort is not None


# ---------------------------------------------------------------------------
# Todos los puertos son Protocols con @runtime_checkable
# ---------------------------------------------------------------------------

def test_job_port_es_protocol_runtime_checkable():
    """JobPort debe ser un Protocol con @runtime_checkable."""
    # runtime_checkable permite isinstance checks
    class FakeJob:
        def create(self, job): ...
        def get(self, job_id): ...
        def list_jobs(self): ...
    assert isinstance(FakeJob(), JobPort)


def test_operational_case_port_es_protocol_runtime_checkable():
    class FakeCase:
        def create_case(self, case): ...
        def get_case(self, case_id): ...
        def list_cases(self): ...
        def update_case_status(self, case_id, status): ...
    assert isinstance(FakeCase(), OperationalCasePort)


def test_report_port_es_protocol_runtime_checkable():
    class FakeReport:
        def create_report(self, report): ...
        def get_report(self, report_id): ...
    assert isinstance(FakeReport(), ReportPort)


def test_decision_port_es_protocol_runtime_checkable():
    class FakeDecision:
        def create(self, decision): ...
        def get(self, decision_id): ...
        def list_decisions(self): ...
    assert isinstance(FakeDecision(), DecisionPort)


def test_evidence_candidate_port_es_protocol_runtime_checkable():
    class FakeEvidence:
        def create(self, candidate): ...
        def get(self, evidence_id): ...
        def list_by_job(self, job_id): ...
    assert isinstance(FakeEvidence(), EvidenceCandidatePort)


def test_cliente_port_es_protocol_runtime_checkable():
    class FakeCliente:
        def get(self, cliente_id): ...
        def exists(self, cliente_id): ...
    assert isinstance(FakeCliente(), ClientePort)


# ---------------------------------------------------------------------------
# Métodos requeridos por puerto
# ---------------------------------------------------------------------------

def test_job_port_tiene_metodos_requeridos():
    methods = _get_method_names(JobPort)
    assert "create" in methods
    assert "get" in methods
    assert "list_jobs" in methods


def test_operational_case_port_tiene_metodos_requeridos():
    methods = _get_method_names(OperationalCasePort)
    assert "create_case" in methods
    assert "get_case" in methods
    assert "list_cases" in methods
    assert "update_case_status" in methods


def test_report_port_tiene_metodos_requeridos():
    methods = _get_method_names(ReportPort)
    assert "create_report" in methods
    assert "get_report" in methods


def test_decision_port_tiene_metodos_requeridos():
    methods = _get_method_names(DecisionPort)
    assert "create" in methods
    assert "get" in methods
    assert "list_decisions" in methods


def test_evidence_candidate_port_tiene_metodos_requeridos():
    methods = _get_method_names(EvidenceCandidatePort)
    assert "create" in methods
    assert "get" in methods
    assert "list_by_job" in methods


def test_cliente_port_tiene_metodos_requeridos():
    methods = _get_method_names(ClientePort)
    assert "get" in methods
    assert "exists" in methods


# ---------------------------------------------------------------------------
# Docstrings codifican el requisito de cliente_id
# ---------------------------------------------------------------------------

def test_job_port_docstring_menciona_cliente_id():
    doc = _get_docstring(JobPort)
    assert "cliente_id" in doc


def test_operational_case_port_docstring_menciona_cliente_id():
    doc = _get_docstring(OperationalCasePort)
    assert "cliente_id" in doc


def test_report_port_docstring_menciona_cliente_id():
    doc = _get_docstring(ReportPort)
    assert "cliente_id" in doc


def test_decision_port_docstring_menciona_cliente_id():
    doc = _get_docstring(DecisionPort)
    assert "cliente_id" in doc


def test_evidence_candidate_port_docstring_menciona_cliente_id():
    doc = _get_docstring(EvidenceCandidatePort)
    assert "cliente_id" in doc


def test_cliente_port_docstring_menciona_cliente_id():
    doc = _get_docstring(ClientePort)
    assert "cliente_id" in doc


# ---------------------------------------------------------------------------
# Docstrings mencionan que Supabase implementará estos puertos
# ---------------------------------------------------------------------------

def test_job_port_docstring_menciona_supabase():
    doc = _get_docstring(JobPort)
    assert "Supabase" in doc or "supabase" in doc


def test_operational_case_port_docstring_menciona_supabase():
    doc = _get_docstring(OperationalCasePort)
    assert "Supabase" in doc or "supabase" in doc


def test_report_port_docstring_menciona_supabase():
    doc = _get_docstring(ReportPort)
    assert "Supabase" in doc or "supabase" in doc


# ---------------------------------------------------------------------------
# Docstrings mencionan que legacy SQLite no es modificado
# ---------------------------------------------------------------------------

def test_job_port_docstring_menciona_legacy_no_modificado():
    doc = _get_docstring(JobPort)
    assert "SQLite" in doc or "legacy" in doc.lower()


def test_operational_case_port_docstring_menciona_legacy_no_modificado():
    doc = _get_docstring(OperationalCasePort)
    assert "SQLite" in doc or "legacy" in doc.lower()


# ---------------------------------------------------------------------------
# Aislamiento: ningún puerto expone operaciones cross-cliente
# ---------------------------------------------------------------------------

def test_job_port_list_no_acepta_cliente_id_externo():
    """list_jobs() no acepta cliente_id como argumento — el aislamiento es por constructor."""
    sig = inspect.signature(JobPort.list_jobs)
    params = list(sig.parameters.keys())
    # Solo 'self' — no hay parámetro cliente_id en list
    assert params == ["self"]


def test_operational_case_port_list_no_acepta_cliente_id_externo():
    """list_cases() no acepta cliente_id como argumento — el aislamiento es por constructor."""
    sig = inspect.signature(OperationalCasePort.list_cases)
    params = list(sig.parameters.keys())
    assert params == ["self"]


def test_decision_port_list_no_acepta_cliente_id_externo():
    """list_decisions() no acepta cliente_id como argumento — el aislamiento es por constructor."""
    sig = inspect.signature(DecisionPort.list_decisions)
    params = list(sig.parameters.keys())
    assert params == ["self"]


# ---------------------------------------------------------------------------
# LaboratorioReportDraft no tiene puerto propio
# ---------------------------------------------------------------------------

def test_no_existe_laboratorio_report_draft_port():
    """LaboratorioReportDraft es transiente — no debe tener puerto de persistencia."""
    import app.repositories.persistence_ports as ports_module
    port_names = [name for name in dir(ports_module) if "Port" in name]
    assert "LaboratorioReportDraftPort" not in port_names
    assert "ReportDraftPort" not in port_names


# ---------------------------------------------------------------------------
# Clase que NO implementa el protocolo no satisface isinstance
# ---------------------------------------------------------------------------

def test_clase_incompleta_no_satisface_job_port():
    """Una clase sin list_jobs no satisface JobPort."""
    class Incompleto:
        def create(self, job): ...
        def get(self, job_id): ...
        # falta list_jobs

    assert not isinstance(Incompleto(), JobPort)


def test_clase_incompleta_no_satisface_operational_case_port():
    """Una clase sin update_case_status no satisface OperationalCasePort."""
    class Incompleto:
        def create_case(self, case): ...
        def get_case(self, case_id): ...
        def list_cases(self): ...
        # falta update_case_status

    assert not isinstance(Incompleto(), OperationalCasePort)
