"""Factory de repositorios P0 para SmartPyme.

Selecciona el adapter correcto (Supabase o SQLite legacy) según el proveedor
configurado en `SMARTPYME_PERSISTENCE_PROVIDER`.

Uso:
    from app.repositories.repository_factory import create_job_repository

    # Supabase (con fake client para tests):
    repo = create_job_repository("cliente-A", provider="supabase", supabase_client=fake)

    # Supabase (con cliente real desde env):
    repo = create_job_repository("cliente-A", provider="supabase")

    # SQLite legacy (requiere db_path):
    repo = create_job_repository("cliente-A", provider="sqlite", db_path="/tmp/smartpyme.db")

    # Desde env (default sqlite):
    repo = create_job_repository("cliente-A")

Reglas:
    - provider se resuelve con get_provider() desde persistence_provider.py.
    - Para repos tenant-scoped, cliente_id es OBLIGATORIO. Fail-closed si vacío.
    - create_cliente_repository() NO requiere cliente_id.
    - Para provider=supabase, supabase_client es inyectable (tests sin red).
    - Para provider=sqlite, se requiere db_path. Si no existe repo SQLite
      equivalente claro para la entidad P0, se lanza NotImplementedError con
      código SQLITE_REPOSITORY_NOT_AVAILABLE_FOR_P0_ENTITY.
    - No introduce tenant_id ni owner_id.
    - No modifica repos SQLite legacy.
    - No hace dual-write.

Mapeo SQLite disponible:
    jobs                → JobRepository (create/get/list_jobs) ✓
    operational_cases   → OperationalCaseRepository (create_case/get_case/list_cases/update_case_status) ✓
    decisions           → DecisionRepository (create/get; list_by_cliente ≠ list_decisions) ⚠ wrapper mínimo
    reports             → NO DISPONIBLE → NotImplementedError
    evidence_candidates → NO DISPONIBLE (EvidenceCandidateRepository usa BemEvidenceCandidate, contrato diferente)
    clientes            → NO DISPONIBLE → NotImplementedError
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from app.repositories.persistence_provider import PersistenceProvider, get_provider

# ---------------------------------------------------------------------------
# Helpers internos
# ---------------------------------------------------------------------------

_SQLITE_NOT_AVAILABLE = "SQLITE_REPOSITORY_NOT_AVAILABLE_FOR_P0_ENTITY"


def _require_cliente_id(cliente_id: str) -> None:
    """Fail-closed si cliente_id está vacío."""
    if not cliente_id or not cliente_id.strip():
        raise ValueError("cliente_id is required")


def _require_db_path(db_path: str | Path | None) -> Path:
    """Fail-closed si db_path no se provee para provider=sqlite."""
    if db_path is None:
        raise ValueError(
            "db_path is required for provider=sqlite. "
            "Provide a valid path to the SQLite database file."
        )
    return Path(db_path)


# ---------------------------------------------------------------------------
# Wrapper mínimo para DecisionRepository → DecisionPort
# ---------------------------------------------------------------------------

class _DecisionRepositorySQLiteAdapter:
    """Adapter mínimo que expone list_decisions() sobre DecisionRepository.

    DecisionRepository tiene list_by_cliente() en lugar de list_decisions().
    Este wrapper agrega el alias sin modificar el repo legacy.
    """

    def __init__(self, inner: Any) -> None:
        self._inner = inner

    def create(self, decision: Any) -> None:
        return self._inner.create(decision)

    def get(self, decision_id: str) -> Any:
        return self._inner.get(decision_id)

    def list_decisions(self) -> list[Any]:
        return self._inner.list_by_cliente()


# ---------------------------------------------------------------------------
# Factory functions
# ---------------------------------------------------------------------------

def create_job_repository(
    cliente_id: str,
    provider: str | None = None,
    supabase_client: Any | None = None,
    db_path: str | Path | None = None,
) -> Any:
    """Crea un repositorio de jobs según el proveedor configurado.

    Args:
        cliente_id: Identificador del tenant. Obligatorio.
        provider: 'sqlite' | 'supabase' | None (lee de env).
        supabase_client: Cliente Supabase inyectable (solo para provider=supabase).
        db_path: Ruta al archivo SQLite (solo para provider=sqlite).

    Returns:
        Instancia que implementa JobPort.

    Raises:
        ValueError: Si cliente_id está vacío.
    """
    _require_cliente_id(cliente_id)
    resolved = get_provider(provider)

    if resolved == PersistenceProvider.SUPABASE:
        from app.repositories.supabase_jobs_repository import SupabaseJobsRepository
        return SupabaseJobsRepository(
            cliente_id=cliente_id,
            supabase_client=supabase_client,
        )

    # SQLite legacy
    path = _require_db_path(db_path)
    from app.repositories.job_repository import JobRepository
    return JobRepository(cliente_id=cliente_id, db_path=path)


def create_operational_case_repository(
    cliente_id: str,
    provider: str | None = None,
    supabase_client: Any | None = None,
    db_path: str | Path | None = None,
) -> Any:
    """Crea un repositorio de operational_cases según el proveedor configurado.

    Args:
        cliente_id: Identificador del tenant. Obligatorio.
        provider: 'sqlite' | 'supabase' | None (lee de env).
        supabase_client: Cliente Supabase inyectable (solo para provider=supabase).
        db_path: Ruta al archivo SQLite (solo para provider=sqlite).

    Returns:
        Instancia que implementa OperationalCasePort.

    Raises:
        ValueError: Si cliente_id está vacío.
    """
    _require_cliente_id(cliente_id)
    resolved = get_provider(provider)

    if resolved == PersistenceProvider.SUPABASE:
        from app.repositories.supabase_operational_cases_repository import (
            SupabaseOperationalCasesRepository,
        )
        return SupabaseOperationalCasesRepository(
            cliente_id=cliente_id,
            supabase_client=supabase_client,
        )

    # SQLite legacy
    path = _require_db_path(db_path)
    from app.repositories.operational_case_repository import OperationalCaseRepository
    return OperationalCaseRepository(cliente_id=cliente_id, db_path=path)


def create_report_repository(
    cliente_id: str,
    provider: str | None = None,
    supabase_client: Any | None = None,
    db_path: str | Path | None = None,
) -> Any:
    """Crea un repositorio de reports según el proveedor configurado.

    Args:
        cliente_id: Identificador del tenant. Obligatorio.
        provider: 'sqlite' | 'supabase' | None (lee de env).
        supabase_client: Cliente Supabase inyectable (solo para provider=supabase).
        db_path: Ruta al archivo SQLite (solo para provider=sqlite, NO DISPONIBLE).

    Returns:
        Instancia que implementa ReportPort.

    Raises:
        ValueError: Si cliente_id está vacío.
        NotImplementedError: Si provider=sqlite (no existe repo SQLite equivalente).
    """
    _require_cliente_id(cliente_id)
    resolved = get_provider(provider)

    if resolved == PersistenceProvider.SUPABASE:
        from app.repositories.supabase_reports_repository import SupabaseReportsRepository
        return SupabaseReportsRepository(
            cliente_id=cliente_id,
            supabase_client=supabase_client,
        )

    # SQLite: no existe repo equivalente claro para DiagnosticReport P0.
    raise NotImplementedError(
        f"{_SQLITE_NOT_AVAILABLE}: reports. "
        "No existe un repositorio SQLite legacy que implemente ReportPort P0. "
        "Usar provider=supabase para esta entidad."
    )


def create_decision_repository(
    cliente_id: str,
    provider: str | None = None,
    supabase_client: Any | None = None,
    db_path: str | Path | None = None,
) -> Any:
    """Crea un repositorio de decisions según el proveedor configurado.

    Args:
        cliente_id: Identificador del tenant. Obligatorio.
        provider: 'sqlite' | 'supabase' | None (lee de env).
        supabase_client: Cliente Supabase inyectable (solo para provider=supabase).
        db_path: Ruta al archivo SQLite (solo para provider=sqlite).

    Returns:
        Instancia que implementa DecisionPort.

    Raises:
        ValueError: Si cliente_id está vacío.
    """
    _require_cliente_id(cliente_id)
    resolved = get_provider(provider)

    if resolved == PersistenceProvider.SUPABASE:
        from app.repositories.supabase_decisions_repository import SupabaseDecisionsRepository
        return SupabaseDecisionsRepository(
            cliente_id=cliente_id,
            supabase_client=supabase_client,
        )

    # SQLite legacy — DecisionRepository tiene list_by_cliente() en lugar de
    # list_decisions(). Se envuelve con _DecisionRepositorySQLiteAdapter.
    path = _require_db_path(db_path)
    from app.repositories.decision_repository import DecisionRepository
    inner = DecisionRepository(cliente_id=cliente_id, db_path=path)
    return _DecisionRepositorySQLiteAdapter(inner)


def create_evidence_candidate_repository(
    cliente_id: str,
    provider: str | None = None,
    supabase_client: Any | None = None,
    db_path: str | Path | None = None,
) -> Any:
    """Crea un repositorio de evidence_candidates según el proveedor configurado.

    Args:
        cliente_id: Identificador del tenant. Obligatorio.
        provider: 'sqlite' | 'supabase' | None (lee de env).
        supabase_client: Cliente Supabase inyectable (solo para provider=supabase).
        db_path: Ruta al archivo SQLite (solo para provider=sqlite, NO DISPONIBLE).

    Returns:
        Instancia que implementa EvidenceCandidatePort.

    Raises:
        ValueError: Si cliente_id está vacío.
        NotImplementedError: Si provider=sqlite (EvidenceCandidateRepository usa
            BemEvidenceCandidate, contrato diferente al EvidenceCandidatePort P0).
    """
    _require_cliente_id(cliente_id)
    resolved = get_provider(provider)

    if resolved == PersistenceProvider.SUPABASE:
        from app.repositories.supabase_evidence_candidates_repository import (
            SupabaseEvidenceCandidatesRepository,
        )
        return SupabaseEvidenceCandidatesRepository(
            cliente_id=cliente_id,
            supabase_client=supabase_client,
        )

    # SQLite: EvidenceCandidateRepository usa BemEvidenceCandidate (contrato BEM),
    # no EvidenceChunk. No es equivalente al EvidenceCandidatePort P0.
    raise NotImplementedError(
        f"{_SQLITE_NOT_AVAILABLE}: evidence_candidates. "
        "EvidenceCandidateRepository usa BemEvidenceCandidate (contrato BEM), "
        "no EvidenceChunk (contrato P0). Usar provider=supabase para esta entidad."
    )


def create_cliente_repository(
    provider: str | None = None,
    supabase_client: Any | None = None,
) -> Any:
    """Crea un repositorio de clientes según el proveedor configurado.

    No requiere cliente_id (este repo consulta clientes por parámetro).

    Args:
        provider: 'sqlite' | 'supabase' | None (lee de env).
        supabase_client: Cliente Supabase inyectable (solo para provider=supabase).

    Returns:
        Instancia que implementa ClientePort.

    Raises:
        NotImplementedError: Si provider=sqlite (no existe repo SQLite de clientes).
    """
    resolved = get_provider(provider)

    if resolved == PersistenceProvider.SUPABASE:
        from app.repositories.supabase_clientes_repository import SupabaseClientesRepository
        return SupabaseClientesRepository(supabase_client=supabase_client)

    # SQLite: no existe repo de clientes en el legacy.
    raise NotImplementedError(
        f"{_SQLITE_NOT_AVAILABLE}: clientes. "
        "No existe un repositorio SQLite legacy para el catálogo de clientes P0. "
        "Usar provider=supabase para esta entidad."
    )
