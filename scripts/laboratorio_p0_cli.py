"""CLI mínimo para ejecutar el flujo Laboratorio P0 con provider configurable."""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

from app.laboratorio_pyme.application_service import LaboratorioApplicationService
from app.laboratorio_pyme.contracts import DiagnosticFinding
from app.laboratorio_pyme.persistence import LaboratorioPersistenceContext
from app.laboratorio_pyme.service import LaboratorioService
from app.laboratorio_pyme.tipos import TipoLaboratorio
from app.repositories.persistence_provider import PersistenceProvider, get_provider

_LAB_ALIAS = {
    "diagnostico_operativo": TipoLaboratorio.analisis_comercial,
}


def _load_env_local_if_exists() -> None:
    env_path = Path(".env.local")
    if not env_path.exists():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        os.environ.setdefault(key.strip(), val.strip())


def _parse_laboratorio(value: str) -> TipoLaboratorio:
    normalized = value.strip()
    if normalized in _LAB_ALIAS:
        return _LAB_ALIAS[normalized]
    try:
        return TipoLaboratorio(normalized)
    except ValueError as exc:
        allowed = [lab.value for lab in TipoLaboratorio] + sorted(_LAB_ALIAS)
        raise argparse.ArgumentTypeError(
            f"laboratorio invalido: '{value}'. Valores permitidos: {allowed}"
        ) from exc


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Ejecuta flujo Laboratorio P0")
    parser.add_argument("--cliente-id", required=True)
    parser.add_argument("--dueno-nombre", required=True)
    parser.add_argument("--laboratorio", required=True, type=_parse_laboratorio)
    parser.add_argument("--hallazgo", required=True)
    parser.add_argument(
        "--provider",
        default=None,
        help="Opcional: sqlite|supabase. Si no se provee, usa SMARTPYME_PERSISTENCE_PROVIDER.",
    )
    parser.add_argument(
        "--db-path",
        default=None,
        help="Ruta SQLite opcional para provider=sqlite.",
    )
    return parser


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
            "metadata": {"created_by": "laboratorio_p0_cli"},
        }
    ).execute()
    if not ctx.clientes.exists(cliente_id):
        raise RuntimeError(f"BLOCKED: no se pudo verificar/crear cliente_id '{cliente_id}'.")


def run_cli(argv: list[str] | None = None) -> int:
    _load_env_local_if_exists()
    args = build_parser().parse_args(argv)
    provider = get_provider(args.provider)

    supabase_client = None
    if provider == PersistenceProvider.SUPABASE:
        supabase_client = _build_supabase_client_from_env()

    ctx = LaboratorioPersistenceContext.from_repository_factory(
        cliente_id=args.cliente_id,
        provider=provider.value,
        supabase_client=supabase_client,
        db_path=args.db_path,
    )

    _ensure_cliente_exists(
        provider=provider,
        ctx=ctx,
        cliente_id=args.cliente_id,
        nombre=args.dueno_nombre,
        supabase_client=supabase_client,
    )

    app_svc = LaboratorioApplicationService(
        laboratorio_service=LaboratorioService(persistence_context=ctx),
        persistence_context=ctx,
    )

    creado = app_svc.crear_caso_persistente(
        cliente_id=args.cliente_id,
        dueno_nombre=args.dueno_nombre,
        laboratorios=[args.laboratorio],
    )
    hallazgo = DiagnosticFinding(
        cliente_id=args.cliente_id,
        finding_id="finding-cli-001",
        case_id=creado.case_id,
        laboratorio=args.laboratorio,
        hallazgo=args.hallazgo,
        prioridad="alta",
        impacto_estimado="CLI_P0",
    )
    cerrado = app_svc.cerrar_caso_persistente(
        cliente_id=args.cliente_id,
        case_id=creado.case_id,
        job_id=creado.job_id,
        hallazgos=[hallazgo],
    )

    print(
        json.dumps(
            {
                "cliente_id": creado.cliente_id,
                "case_id": creado.case_id,
                "job_id": creado.job_id,
                "report_id": cerrado.report_id,
                "status": "closed",
            },
            ensure_ascii=True,
        )
    )
    return 0


def main() -> None:
    try:
        raise SystemExit(run_cli())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()

