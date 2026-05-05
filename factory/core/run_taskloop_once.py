#!/usr/bin/env python3
"""Entrypoint mínimo para ejecutar un ciclo del TaskLoop soberano.

Este módulo proporciona una CLI simple que invoca run_one_queued_task()
con use_sovereign=True, respetando los paths por defecto del Factory.

Uso:

    python3 -m factory.core.run_taskloop_once --mode sovereign
    python3 -m factory.core.run_taskloop_once --mode multiagent

Opcionalmente se pueden sobreescribir los paths:

    --tasks-dir /ruta/taskspecs
    --evidence-dir /ruta/evidence/taskspecs
    --gate-path /ruta/AUDIT_GATE.md
    --repo-root /ruta/del/repo

La salida es un objeto JSON compacto con el resultado del ciclo.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from factory.core.queue_runner import run_one_queued_task


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="factory.core.run_taskloop_once",
        description="Ejecuta un ciclo del TaskLoop soberano de SmartPyme Factory.",
        epilog="Defaults: tasks_dir='factory/taskspecs', evidence_dir='factory/evidence/taskspecs', gate_path='factory/control/AUDIT_GATE.md'",
    )
    parser.add_argument(
        "--mode",
        choices=["sovereign", "multiagent"],
        default="sovereign",
        help="Tipo de runner a usar (default: sovereign)",
    )
    parser.add_argument(
        "--tasks-dir",
        default="factory/taskspecs",
        help="Directorio raíz de TaskSpecs (default: factory/taskspecs)",
    )
    parser.add_argument(
        "--evidence-dir",
        default="factory/evidence/taskspecs",
        help="Directorio base para evidencias (default: factory/evidence/taskspecs)",
    )
    parser.add_argument(
        "--gate-path",
        default="factory/control/AUDIT_GATE.md",
        help="Ruta al archivo de control AUDIT_GATE.md (default: factory/control/AUDIT_GATE.md)",
    )
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Raíz del repositorio (default: directorio actual)",
    )
    parser.add_argument(
        "--compact",
        action="store_true",
        help="Salida JSON sin indentación (default: indentado)",
    )

    args = parser.parse_args()

    result = run_one_queued_task(
        tasks_dir=args.tasks_dir,
        evidence_dir=args.evidence_dir,
        use_sovereign=(args.mode == "sovereign"),
        gate_path=args.gate_path,
        repo_root=args.repo_root,
    )

    # Filtrar campos no requeridos por el contrato solicitado
    # run_one_queued_task devuelve 'reason' o 'blocking_reason'; preferimos 'blocking_reason'
    filtered = {
        "status": result.get("status"),
        "task_id": result.get("task_id"),
        "evidence_dir": result.get("evidence_dir"),
        "evidence_manifest_path": result.get("evidence_manifest_path"),
        "execution_result_path": result.get("execution_result_path"),
        "audit_decision_path": result.get("audit_decision_path"),
        "human_escalation_path": result.get("human_escalation_path"),
        "blocking_reason": result.get("blocking_reason") or result.get("reason"),
        "gate_status": result.get("gate_status"),
    }

    indent = None if args.compact else 2
    json.dump(filtered, sys.stdout, ensure_ascii=False, indent=indent)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()