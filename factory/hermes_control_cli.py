#!/usr/bin/env python3
"""Control operativo seguro para SmartPyme Factory via Hermes Gateway.

Este archivo NO es un runner autonomo ni un bot paralelo.
Es una herramienta invocable por Hermes Gateway mediante quick_commands.

Comandos soportados:
- estado
- actualizar
- pausar
- reanudar
- avanzar
- auditar

Reglas:
- castellano operativo;
- fail-closed ante incertidumbre;
- no reactivar scripts legacy.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

REPO_DEFAULT = Path("/opt/smartpyme-factory/repos/SmartPyme")
HERMES_HOME_DEFAULT = Path("/home/neoalmasana/.hermes")
HERMES_CLI_DEFAULT = HERMES_HOME_DEFAULT / "venv/bin/hermes"

BLOQUEANTES = {"WAITING_AUDIT", "BLOCKED", "HOLD", "PAUSED"}
LEGACY_PATTERNS = ("telegram_factory_control.py", "hermes_factory_runner.py")


@dataclass
class Resultado:
    comando_recibido: str
    decision: str
    estado_repo: str
    estado_gate: str
    tarea_seleccionada: str
    evidencia_generada: str
    errores: str
    proximo_paso: str

    def texto(self) -> str:
        return "\n".join(f"{k}: {v}" for k, v in asdict(self).items())


def ahora_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def repo_path() -> Path:
    return Path(os.getenv("SMARTPYME_REPO", str(REPO_DEFAULT)))


def hermes_cli_path() -> Path:
    return Path(os.getenv("HERMES_CLI", str(HERMES_CLI_DEFAULT)))


def run_cmd(args: list[str], cwd: Path | None = None, timeout: int = 60) -> tuple[int, str]:
    try:
        proc = subprocess.run(
            args,
            cwd=str(cwd) if cwd else None,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
        out = (proc.stdout or "") + (proc.stderr or "")
        return proc.returncode, out.strip()
    except Exception as exc:  # pragma: no cover - defensa operativa
        return 1, f"ERROR_EJECUCION: {exc}"


def leer_texto(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except FileNotFoundError:
        return ""


def git_status(repo: Path) -> str:
    code, out = run_cmd(["git", "status", "--short"], cwd=repo)
    if code != 0:
        return f"ERROR git status: {out}"
    return out or "limpio"


def git_log(repo: Path) -> str:
    code, out = run_cmd(["git", "log", "--oneline", "-5"], cwd=repo)
    if code != 0:
        return f"ERROR git log: {out}"
    return out or "sin commits visibles"


def git_pull(repo: Path) -> tuple[bool, str]:
    code, out = run_cmd(["git", "pull", "--ff-only", "origin", "main"], cwd=repo, timeout=120)
    return code == 0, out


def procesos_legacy() -> str:
    code, out = run_cmd(["ps", "-ef"])
    if code != 0:
        return f"ERROR ps: {out}"
    current_pid = str(os.getpid())
    lineas = []
    for line in out.splitlines():
        if current_pid in line:
            continue
        if any(p in line for p in LEGACY_PATTERNS):
            lineas.append(line)
    return "\n".join(lineas) if lineas else "ninguno"


def gateway_status() -> str:
    hermes = hermes_cli_path()
    if not hermes.exists():
        return f"Hermes CLI no existe: {hermes}"
    code, out = run_cmd([str(hermes), "gateway", "status"], cwd=Path.home(), timeout=30)
    if code != 0:
        return f"ERROR gateway status: {out}"
    return out or "sin salida"


def extraer_campo_estado(texto: str, campo: str) -> str | None:
    """Lee un campo YAML simple por nombre exacto."""
    patron = re.compile(rf"^\s*{re.escape(campo)}\s*:\s*(.*?)\s*$", re.IGNORECASE)
    for line in texto.splitlines():
        match = patron.match(line)
        if match:
            valor = match.group(1).strip().strip("'\"")
            return valor or None
    return None


def leer_gate(repo: Path) -> str:
    candidatos = [
        repo / "factory/control/AUDIT_GATE.md",
        repo / "factory/control/FACTORY_STATUS.md",
    ]
    partes: list[str] = []
    for path in candidatos:
        texto = leer_texto(path).strip()
        if texto:
            partes.append(f"{path.name}: {texto[:500]}")
    return "\n".join(partes) if partes else "sin gate visible"


def contiene_estado_bloqueante(texto: str) -> str | None:
    upper = texto.upper()
    for estado in sorted(BLOQUEANTES):
        if estado in upper:
            return estado
    return None


def estado_bloqueante_actual(repo: Path) -> str | None:
    """Evalua solo campos actuales de control, no menciones historicas."""
    factory_status = leer_texto(repo / "factory/control/FACTORY_STATUS.md")
    audit_gate = leer_texto(repo / "factory/control/AUDIT_GATE.md")

    estado = extraer_campo_estado(factory_status, "estado")
    if estado and estado.upper() in BLOQUEANTES:
        return estado.upper()

    status = extraer_campo_estado(audit_gate, "status")
    if status and status.upper() in BLOQUEANTES:
        return status.upper()

    return None


def escribir_estado(repo: Path, estado: str, motivo: str) -> Path:
    control = repo / "factory/control"
    control.mkdir(parents=True, exist_ok=True)
    path = control / "FACTORY_STATUS.md"
    path.write_text(
        "# Estado SmartPyme Factory\n\n"
        f"estado: {estado}\n"
        f"motivo: {motivo}\n"
        f"actualizado_en: {ahora_iso()}\n",
        encoding="utf-8",
    )
    return path


def seleccionar_task_pending(repo: Path) -> str:
    tasks_dir = repo / "factory/ai_governance/tasks"
    if not tasks_dir.exists():
        return "ninguna: no existe factory/ai_governance/tasks"
    for path in sorted(tasks_dir.glob("*.yaml")):
        texto = leer_texto(path)
        if extraer_campo_estado(texto, "status") == "pending" or "status: pending" in texto:
            return str(path)
    return "ninguna"


def escribir_evidencia_bloqueo(repo: Path, task_path: str, motivo: str, pull_out: str) -> str:
    task_id = (
        Path(task_path).stem
        if task_path and not task_path.startswith("ninguna")
        else "sin_task"
    )
    evidence_dir = repo / "factory/evidence" / task_id
    evidence_dir.mkdir(parents=True, exist_ok=True)
    (evidence_dir / "control_preflight.txt").write_text(
        f"fecha={ahora_iso()}\n"
        f"repo={repo}\n"
        f"task={task_path}\n"
        f"pull={pull_out}\n"
        f"decision=BLOCKED\n"
        f"motivo={motivo}\n",
        encoding="utf-8",
    )
    (evidence_dir / "decision.txt").write_text(f"BLOCKED\n{motivo}\n", encoding="utf-8")
    return str(evidence_dir)


def comando_estado() -> Resultado:
    repo = repo_path()
    errores = []
    if not repo.exists():
        errores.append(f"repo no existe: {repo}")
    legacy = procesos_legacy()
    if legacy != "ninguno":
        errores.append(f"procesos legacy activos: {legacy}")
    return Resultado(
        comando_recibido="/estado",
        decision="BLOCKED" if errores else "OK",
        estado_repo=(
            f"ruta={repo}; "
            f"status={git_status(repo) if repo.exists() else 'no disponible'}; "
            f"log={git_log(repo) if repo.exists() else 'no disponible'}; "
            f"gateway={gateway_status()}"
        ),
        estado_gate=leer_gate(repo) if repo.exists() else "no disponible",
        tarea_seleccionada="ninguna",
        evidencia_generada="ninguna",
        errores="; ".join(errores) if errores else "ninguno",
        proximo_paso="corregir errores" if errores else "usar /avanzar o /actualizar",
    )


def comando_actualizar() -> Resultado:
    repo = repo_path()
    if not repo.exists():
        return Resultado(
            "/actualizar",
            "BLOCKED",
            f"repo no existe: {repo}",
            "no disponible",
            "ninguna",
            "ninguna",
            "repo inexistente",
            "verificar MAPA_RUTAS_REPOS_GCP.md",
        )
    ok, out = git_pull(repo)
    return Resultado(
        comando_recibido="/actualizar",
        decision="OK" if ok else "BLOCKED",
        estado_repo=out,
        estado_gate=leer_gate(repo),
        tarea_seleccionada="ninguna",
        evidencia_generada="ninguna",
        errores="ninguno" if ok else out,
        proximo_paso="usar /estado o /avanzar" if ok else "resolver pull fallido",
    )


def comando_pausar() -> Resultado:
    repo = repo_path()
    if not repo.exists():
        return Resultado(
            "/pausar",
            "BLOCKED",
            f"repo no existe: {repo}",
            "no disponible",
            "ninguna",
            "ninguna",
            "repo inexistente",
            "verificar ruta absoluta",
        )
    path = escribir_estado(repo, "PAUSED", "pausa solicitada por owner desde Telegram/Hermes")
    return Resultado(
        "/pausar",
        "OK",
        git_status(repo),
        leer_gate(repo),
        "ninguna",
        str(path),
        "ninguno",
        "usar /reanudar para abrir la factoria",
    )


def comando_reanudar() -> Resultado:
    repo = repo_path()
    if not repo.exists():
        return Resultado(
            "/reanudar",
            "BLOCKED",
            f"repo no existe: {repo}",
            "no disponible",
            "ninguna",
            "ninguna",
            "repo inexistente",
            "verificar ruta absoluta",
        )
    bloqueante = estado_bloqueante_actual(repo)
    if bloqueante in {"WAITING_AUDIT", "BLOCKED", "HOLD"}:
        return Resultado(
            "/reanudar",
            "BLOCKED",
            git_status(repo),
            leer_gate(repo),
            "ninguna",
            "ninguna",
            f"gate bloqueante: {bloqueante}",
            "auditar o desbloquear manualmente",
        )
    path = escribir_estado(repo, "OPEN", "reanudar solicitada por owner desde Telegram/Hermes")
    return Resultado(
        "/reanudar",
        "OK",
        git_status(repo),
        leer_gate(repo),
        "ninguna",
        str(path),
        "ninguno",
        "usar /avanzar para ejecutar un ciclo",
    )


def comando_avanzar() -> Resultado:
    repo = repo_path()
    if not repo.exists():
        return Resultado(
            "/avanzar",
            "BLOCKED",
            f"repo no existe: {repo}",
            "no disponible",
            "ninguna",
            "ninguna",
            "repo inexistente",
            "verificar MAPA_RUTAS_REPOS_GCP.md",
        )

    ok, pull_out = git_pull(repo)
    if not ok:
        return Resultado(
            "/avanzar",
            "BLOCKED",
            pull_out,
            leer_gate(repo),
            "ninguna",
            "ninguna",
            "fallo git pull --ff-only origin main",
            "resolver conflicto de git",
        )

    legacy = procesos_legacy()
    if legacy != "ninguno":
        return Resultado(
            "/avanzar",
            "BLOCKED",
            pull_out,
            leer_gate(repo),
            "ninguna",
            "ninguna",
            f"procesos legacy activos: {legacy}",
            "detener contaminacion legacy",
        )

    bloqueante = estado_bloqueante_actual(repo)
    if bloqueante:
        return Resultado(
            "/avanzar",
            "BLOCKED",
            pull_out,
            leer_gate(repo),
            "ninguna",
            "ninguna",
            f"gate bloqueante: {bloqueante}",
            "usar /auditar, /reanudar o resolver bloqueo",
        )

    task = seleccionar_task_pending(repo)
    if task == "ninguna" or task.startswith("ninguna:"):
        return Resultado(
            "/avanzar",
            "BLOCKED",
            pull_out,
            leer_gate(repo),
            task,
            "ninguna",
            "no hay TaskSpec pending",
            "crear una TaskSpec pending",
        )

    # P0-5 / TASK-AVANZAR-DISPATCH-001:
    # Este bloqueo es intencional y fail-closed. No debe reemplazarse por dispatch real
    # hasta que existan cinco requisitos verificables:
    # 1) Builder real invocable por Hermes Gateway, sin runners legacy.
    # 2) Validacion estricta de TaskSpec contra schema antes de cualquier cambio.
    # 3) Control de allowed_files / forbidden_files antes de delegar.
    # 4) Evidencia reproducible en factory/evidence/<task_id>/ para comandos, diff y tests.
    # 5) Gate de auditoria externo que impida nuevo dispatch hasta decision humana/GPT.
    motivo = "DISPATCH_REAL_NO_IMPLEMENTADO_SIN_BUILDER_VERIFICABLE"
    evidencia = escribir_evidencia_bloqueo(repo, task, motivo, pull_out)
    escribir_estado(repo, "BLOCKED", motivo)

    return Resultado(
        "/avanzar",
        "BLOCKED",
        pull_out,
        leer_gate(repo),
        task,
        evidencia,
        motivo,
        "implementar dispatch real bajo TASK-AVANZAR-DISPATCH-001 antes de ejecutar cambios",
    )


def comando_auditar() -> Resultado:
    repo = repo_path()
    if not repo.exists():
        return Resultado(
            "/auditar",
            "BLOCKED",
            f"repo no existe: {repo}",
            "no disponible",
            "ninguna",
            "ninguna",
            "repo inexistente",
            "verificar ruta absoluta",
        )
    evidence = repo / "factory/evidence"
    recientes = []
    if evidence.exists():
        recientes = [
            str(p)
            for p in sorted(
                evidence.iterdir(),
                key=lambda p: p.stat().st_mtime,
                reverse=True,
            )[:5]
        ]
    decision = "NEEDS_REVIEW" if not recientes else "BLOCKED"
    return Resultado(
        "/auditar",
        decision,
        git_status(repo),
        leer_gate(repo),
        "ninguna",
        "\n".join(recientes) if recientes else "ninguna",
        "sin evidencia" if not recientes else "auditoria humana requerida",
        "ChatGPT Director-Auditor debe revisar evidencia y emitir dictamen",
    )


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Control seguro de SmartPyme Factory para Hermes")
    parser.add_argument(
        "comando",
        choices=["estado", "actualizar", "pausar", "reanudar", "avanzar", "auditar"],
    )
    parser.add_argument("--json", action="store_true", help="Emitir JSON en vez de texto")
    args = parser.parse_args(list(argv) if argv is not None else None)

    handlers = {
        "estado": comando_estado,
        "actualizar": comando_actualizar,
        "pausar": comando_pausar,
        "reanudar": comando_reanudar,
        "avanzar": comando_avanzar,
        "auditar": comando_auditar,
    }
    resultado = handlers[args.comando]()
    if args.json:
        print(json.dumps(asdict(resultado), ensure_ascii=False, indent=2))
    else:
        print(resultado.texto())
    return 0 if resultado.decision in {"OK", "APPROVED"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
