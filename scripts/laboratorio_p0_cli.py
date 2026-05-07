"""CLI mínimo para ejecutar el flujo Laboratorio P0 con provider configurable."""
from __future__ import annotations

import argparse
import json
import sys

from app.laboratorio_pyme.p0_runner import parse_laboratorio, run_laboratorio_p0


def _parse_laboratorio_arg(value: str) -> str:
    try:
        parse_laboratorio(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"laboratorio invalido: '{value}'") from exc
    return value


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Ejecuta flujo Laboratorio P0")
    parser.add_argument("--cliente-id", required=True)
    parser.add_argument("--dueno-nombre", required=True)
    parser.add_argument("--laboratorio", required=True, type=_parse_laboratorio_arg)
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


def run_cli(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = run_laboratorio_p0(
        cliente_id=args.cliente_id,
        dueno_nombre=args.dueno_nombre,
        laboratorio=args.laboratorio,
        hallazgo=args.hallazgo,
        provider=args.provider,
        db_path=args.db_path,
    )
    print(json.dumps(result.to_dict(), ensure_ascii=True))
    return 0


def main() -> None:
    try:
        raise SystemExit(run_cli())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()

