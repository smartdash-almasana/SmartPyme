"""Puertos de persistencia P0 para SmartPyme.

Define los contratos (interfaces/protocolos) que deben implementar los adapters
de persistencia para las 6 entidades core P0:

    - jobs              (background_jobs)
    - operational_cases
    - reports           (diagnostic_reports)
    - decisions         (decision_records)
    - evidence_candidates
    - clientes

Reglas de diseño:
    - cliente_id es OBLIGATORIO en todas las operaciones de lectura y escritura.
    - Todos los puertos están ligados a un cliente_id en el constructor o en
      cada método — no existe operación cross-cliente.
    - Los repositorios SQLite legacy NO son modificados en este paso.
    - El adapter Supabase implementará estos puertos en Step 3+.
    - Prohibido usar tenant_id u owner_id como alias de cliente_id.
    - LaboratorioReportDraft NO tiene puerto propio — es un objeto transiente.

Uso esperado (Step 3+):
    class SupabaseJobPort(JobPort):
        def __init__(self, cliente_id: str, ...): ...
        def create(self, job: Job) -> None: ...
        ...

Solo stdlib. Sin dependencias externas.
"""
from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


# ---------------------------------------------------------------------------
# JobPort — puerto para entidad jobs (background_jobs)
# ---------------------------------------------------------------------------

@runtime_checkable
class JobPort(Protocol):
    """Puerto de persistencia para jobs (background_jobs).

    cliente_id es obligatorio y debe ser el primer argumento del constructor.
    Todas las operaciones están aisladas por cliente_id.
    El adapter Supabase implementará este puerto en Step 3.
    Los repositorios SQLite legacy no son modificados.
    """

    def create(self, job: Any) -> None:
        """Persiste un nuevo job.

        Args:
            job: Instancia de Job. job.cliente_id debe coincidir con el
                 cliente_id del adapter (fail-closed ante mismatch).
        """
        ...

    def get(self, job_id: str) -> Any | None:
        """Recupera un job por job_id, filtrado por cliente_id del adapter.

        Returns:
            Instancia de Job o None si no existe para este cliente.
        """
        ...

    def list_jobs(self) -> list[Any]:
        """Lista todos los jobs del cliente_id del adapter.

        Returns:
            Lista de instancias de Job. Nunca retorna jobs de otros clientes.
        """
        ...


# ---------------------------------------------------------------------------
# OperationalCasePort — puerto para entidad operational_cases
# ---------------------------------------------------------------------------

@runtime_checkable
class OperationalCasePort(Protocol):
    """Puerto de persistencia para operational_cases.

    cliente_id es obligatorio y debe ser el primer argumento del constructor.
    Todas las operaciones están aisladas por cliente_id.
    El adapter Supabase implementará este puerto en Step 3.
    Los repositorios SQLite legacy no son modificados.
    """

    def create_case(self, case: Any) -> None:
        """Persiste un nuevo caso operacional.

        Args:
            case: Instancia de OperationalCase. case.cliente_id debe coincidir
                  con el cliente_id del adapter (fail-closed ante mismatch).
        """
        ...

    def get_case(self, case_id: str) -> Any | None:
        """Recupera un caso por case_id, filtrado por cliente_id del adapter.

        Returns:
            Instancia de OperationalCase o None si no existe para este cliente.
        """
        ...

    def list_cases(self) -> list[Any]:
        """Lista todos los casos del cliente_id del adapter.

        Returns:
            Lista de instancias de OperationalCase. Nunca retorna casos de otros clientes.
        """
        ...

    def update_case_status(self, case_id: str, status: str) -> bool:
        """Actualiza el estado de un caso.

        Args:
            case_id: Identificador del caso.
            status: Nuevo estado. Debe ser un valor válido del dominio.

        Returns:
            True si la actualización fue exitosa, False si el caso no existe
            para este cliente o el estado es inválido.
        """
        ...


# ---------------------------------------------------------------------------
# ReportPort — puerto para entidad reports (diagnostic_reports)
# ---------------------------------------------------------------------------

@runtime_checkable
class ReportPort(Protocol):
    """Puerto de persistencia para reports (diagnostic_reports).

    cliente_id es obligatorio y debe ser el primer argumento del constructor.
    Todas las operaciones están aisladas por cliente_id.
    El adapter Supabase implementará este puerto en Step 4.
    Los repositorios SQLite legacy no son modificados.
    """

    def create_report(self, report: Any) -> None:
        """Persiste un nuevo reporte diagnóstico.

        Args:
            report: Instancia de DiagnosticReport. report.cliente_id debe
                    coincidir con el cliente_id del adapter.
        """
        ...

    def get_report(self, report_id: str) -> Any | None:
        """Recupera un reporte por report_id, filtrado por cliente_id del adapter.

        Returns:
            Instancia de DiagnosticReport o None si no existe para este cliente.
        """
        ...


# ---------------------------------------------------------------------------
# DecisionPort — puerto para entidad decisions (decision_records)
# ---------------------------------------------------------------------------

@runtime_checkable
class DecisionPort(Protocol):
    """Puerto de persistencia para decisions (decision_records).

    cliente_id es obligatorio y debe ser el primer argumento del constructor.
    Todas las operaciones están aisladas por cliente_id.
    El adapter Supabase implementará este puerto en Step 4.
    Los repositorios SQLite legacy no son modificados.
    """

    def create(self, decision: Any) -> None:
        """Persiste una nueva decisión.

        Args:
            decision: Instancia de DecisionRecord. decision.cliente_id debe
                      coincidir con el cliente_id del adapter.
        """
        ...

    def get(self, decision_id: str) -> Any | None:
        """Recupera una decisión por decision_id, filtrado por cliente_id del adapter.

        Returns:
            Instancia de DecisionRecord o None si no existe para este cliente.
        """
        ...

    def list_decisions(self) -> list[Any]:
        """Lista todas las decisiones del cliente_id del adapter.

        Returns:
            Lista de instancias de DecisionRecord. Nunca retorna decisiones de otros clientes.
        """
        ...


# ---------------------------------------------------------------------------
# EvidenceCandidatePort — puerto para entidad evidence_candidates
# ---------------------------------------------------------------------------

@runtime_checkable
class EvidenceCandidatePort(Protocol):
    """Puerto de persistencia para evidence_candidates.

    cliente_id es obligatorio y debe ser el primer argumento del constructor.
    Todas las operaciones están aisladas por cliente_id.
    El adapter Supabase implementará este puerto en Step 5.
    Los repositorios SQLite legacy no son modificados.
    """

    def create(self, candidate: Any) -> None:
        """Persiste un nuevo candidato de evidencia.

        Args:
            candidate: Instancia de EvidenceChunk o ExtractedFactCandidate.
                       candidate.cliente_id debe coincidir con el cliente_id del adapter.
        """
        ...

    def get(self, evidence_id: str) -> Any | None:
        """Recupera un candidato por evidence_id, filtrado por cliente_id del adapter.

        Returns:
            Instancia del candidato o None si no existe para este cliente.
        """
        ...

    def list_by_job(self, job_id: str) -> list[Any]:
        """Lista candidatos de evidencia para un job específico del cliente.

        Args:
            job_id: Identificador del job. Solo retorna candidatos de este
                    cliente y este job.

        Returns:
            Lista de candidatos. Nunca retorna evidencia de otros clientes.
        """
        ...


# ---------------------------------------------------------------------------
# ClientePort — puerto para entidad clientes (catálogo de identidad mínimo)
# ---------------------------------------------------------------------------

@runtime_checkable
class ClientePort(Protocol):
    """Puerto de persistencia para clientes (catálogo de identidad mínimo P0).

    Proporciona FK lógica para aislamiento multi-cliente.
    El adapter Supabase implementará este puerto en Step 5.
    Los repositorios SQLite legacy no son modificados.

    Nota: cliente_id es la clave soberana. Prohibido usar tenant_id u owner_id.
    """

    def get(self, cliente_id: str) -> Any | None:
        """Recupera un cliente por cliente_id.

        Args:
            cliente_id: Identificador único del cliente. Obligatorio.

        Returns:
            Registro del cliente o None si no existe.
        """
        ...

    def exists(self, cliente_id: str) -> bool:
        """Verifica si un cliente existe en el catálogo.

        Args:
            cliente_id: Identificador único del cliente. Obligatorio.

        Returns:
            True si el cliente existe, False en caso contrario.
        """
        ...
