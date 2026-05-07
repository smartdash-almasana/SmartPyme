"""Integración mínima de Laboratorio MVP con repository_factory P0.

Esta capa no toca Supabase real ni persiste por sí misma objetos transientes
del Laboratorio. Solo resuelve e inyecta repositorios core P0.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.repositories.repository_factory import (
    create_cliente_repository,
    create_decision_repository,
    create_evidence_candidate_repository,
    create_job_repository,
    create_operational_case_repository,
    create_report_repository,
)


@dataclass(frozen=True, slots=True)
class LaboratorioPersistenceContext:
    """Contenedor de repositorios P0 resueltos para un cliente."""

    cliente_id: str
    jobs: Any
    operational_cases: Any
    reports: Any
    decisions: Any
    evidence_candidates: Any
    clientes: Any

    @classmethod
    def from_repository_factory(
        cls,
        *,
        cliente_id: str,
        provider: str | None = None,
        supabase_client: Any | None = None,
        db_path: str | Path | None = None,
    ) -> "LaboratorioPersistenceContext":
        """Resuelve repositorios P0 usando el factory oficial.

        Respeta provider explícito o env. Si una entidad no tiene soporte en
        SQLite P0, se mantiene el fail-closed del factory (NotImplementedError).
        """
        return cls(
            cliente_id=cliente_id,
            jobs=create_job_repository(
                cliente_id=cliente_id,
                provider=provider,
                supabase_client=supabase_client,
                db_path=db_path,
            ),
            operational_cases=create_operational_case_repository(
                cliente_id=cliente_id,
                provider=provider,
                supabase_client=supabase_client,
                db_path=db_path,
            ),
            reports=create_report_repository(
                cliente_id=cliente_id,
                provider=provider,
                supabase_client=supabase_client,
                db_path=db_path,
            ),
            decisions=create_decision_repository(
                cliente_id=cliente_id,
                provider=provider,
                supabase_client=supabase_client,
                db_path=db_path,
            ),
            evidence_candidates=create_evidence_candidate_repository(
                cliente_id=cliente_id,
                provider=provider,
                supabase_client=supabase_client,
                db_path=db_path,
            ),
            clientes=create_cliente_repository(
                provider=provider,
                supabase_client=supabase_client,
            ),
        )

