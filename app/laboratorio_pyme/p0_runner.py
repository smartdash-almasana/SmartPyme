"""Runner compartido para flujo Laboratorio P0 (CLI + endpoint)."""
from __future__ import annotations

import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from app.laboratorio_pyme.application_service import LaboratorioApplicationService
from app.laboratorio_pyme.contracts import DiagnosticFinding
from app.laboratorio_pyme.persistence import LaboratorioPersistenceContext
from app.laboratorio_pyme.service import LaboratorioService
from app.laboratorio_pyme.tipos import TipoLaboratorio
from app.repositories.persistence_provider import PersistenceProvider, get_provider


@dataclass(frozen=True, slots=True)
class LaboratorioP0Result:
    cliente_id: str
    case_id: str
    job_id: str
    report_id: str
    status: str = "closed"

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


def load_env_local_if_exists() -> None:
    env_path = Path(".env.local")
    if not env_path.exists():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        os.environ.setdefault(key.strip(), val.strip())


def parse_laboratorio(value: str) -> TipoLaboratorio:
    aliases = {"diagnostico_operativo": TipoLaboratorio.analisis_comercial}
    normalized = value.strip()
    if normalized in aliases:
        return aliases[normalized]
    return TipoLaboratorio(normalized)


def _build_supabase_client_from_env() -> Any:
    try:
        from supabase import create_client
    except ImportError as exc:
        raise RuntimeError(
            "BLOCKED_MISSING_DEPENDENCY: libreria 'supabase' no instalada."
        ) from exc

    url = os.environ.get("SMARTPYME_SUPABASE_URL", "").strip()
    key = os.environ.get("SMARTPYME_SUPABASE_KEY", "").strip()
    if not url or not key:
        raise RuntimeError(
            "BLOCKED_ENVIRONMENT_CONTRACT_MISSING: faltan SMARTPYME_SUPABASE_URL/KEY."
        )
    return create_client(url, key)


def _ensure_cliente_exists(
    *,
    provider: PersistenceProvider,
    ctx: LaboratorioPersistenceContext,
    cliente_id: str,
    nombre: str,
    supabase_client: Any | None,
) -> None:
    if provider != PersistenceProvider.SUPABASE:
        return
    if ctx.clientes.exists(cliente_id):
        return
    if supabase_client is None:
        raise RuntimeError("BLOCKED: no se pudo construir cliente Supabase para alta de cliente.")
    supabase_client.table("clientes").insert(
        {
            "cliente_id": cliente_id,
            "nombre": nombre,
            "status": "active",
            "metadata": {"created_by": "laboratorio_p0_runner"},
        }
    ).execute()
    if not ctx.clientes.exists(cliente_id):
        raise RuntimeError(f"BLOCKED: no se pudo verificar/crear cliente_id '{cliente_id}'.")


def run_laboratorio_p0(
    *,
    cliente_id: str,
    dueno_nombre: str,
    laboratorio: str,
    hallazgo: str,
    provider: str | None = None,
    db_path: str | None = None,
    load_env_local: bool = True,
) -> LaboratorioP0Result:
    if load_env_local:
        load_env_local_if_exists()

    resolved_provider = get_provider(provider)
    laboratorio_tipo = parse_laboratorio(laboratorio)

    supabase_client = None
    if resolved_provider == PersistenceProvider.SUPABASE:
        supabase_client = _build_supabase_client_from_env()

    ctx = LaboratorioPersistenceContext.from_repository_factory(
        cliente_id=cliente_id,
        provider=resolved_provider.value,
        supabase_client=supabase_client,
        db_path=db_path,
    )

    _ensure_cliente_exists(
        provider=resolved_provider,
        ctx=ctx,
        cliente_id=cliente_id,
        nombre=dueno_nombre,
        supabase_client=supabase_client,
    )

    app_svc = LaboratorioApplicationService(
        laboratorio_service=LaboratorioService(persistence_context=ctx),
        persistence_context=ctx,
    )
    creado = app_svc.crear_caso_persistente(
        cliente_id=cliente_id,
        dueno_nombre=dueno_nombre,
        laboratorios=[laboratorio_tipo],
    )
    finding = DiagnosticFinding(
        cliente_id=cliente_id,
        finding_id="finding-cli-001",
        case_id=creado.case_id,
        laboratorio=laboratorio_tipo,
        hallazgo=hallazgo,
        prioridad="alta",
        impacto_estimado="CLI_P0",
    )
    cerrado = app_svc.cerrar_caso_persistente(
        cliente_id=cliente_id,
        case_id=creado.case_id,
        job_id=creado.job_id,
        hallazgos=[finding],
    )
    return LaboratorioP0Result(
        cliente_id=creado.cliente_id,
        case_id=creado.case_id,
        job_id=creado.job_id,
        report_id=cerrado.report_id,
        status="closed",
    )

