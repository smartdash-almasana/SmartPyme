#!/usr/bin/env python3
"""Control operativo seguro para SmartPyme Factory vía Hermes.

Este archivo NO es un runner autónomo ni un bot paralelo.
Es una herramienta invocable por Hermes para ejecutar comandos de control
acotados: estado, actualizar, pausar, reanudar, avanzar y auditar.

Todos los comandos responden en castellano y usan rutas absolutas por defecto.
"""

from __future__ import annotations

import argparse
import json
import os
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
        data = asdict(self)
        return "\n".join(f"{k}: {v}" for k, v in data.items())


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


def extraer_campo_estado(texto: str, campo: str) -> str | None:
    """Extrae un estado actual desde una línea exacta tipo `status:` o `estado:`.

    Importante: no toma campos historicos como `audit_gate:` o `last_error:`.
    Esto evita que un `FACTORY_STATUS.md` viejo bloquee cuando `AUDIT_GATE.md`
    ya fue reabierto correctamente.
    """
    prefijo = f"{campo}:"
    for linea in texto.splitlines():
        limpia = linea.strip()
        if limpia.lower().startswith(prefijo):
            valor = limpia.split(":", 1)[1].strip().upper()
            return valor or None
    return None


def audit_gate_status(repo: Path) -> str | None:
    return extraer_campo_estado(leer_texto(repo / "factory/control/AUDIT_GATE.md"), "status")


def factory_status_actual(repo: Path) -> str | None:
    return extraer_campo_estado(leer_texto(repo / "factory/control/FACTORY_STATUS.md"), "estado")


def estado_bloqueante_actual(repo: Path) -> str | None:
    """Devuelve bloqueo actual, ignorando trazas historicas no normativas."""
    audit = audit_gate_status(repo)
    if audit in BLOQUEANTES:
        return audit

    estado = factory_status_actual(repo)
    if estado in {"PAUSED", "HOLD", "BLOCKED"}:
        return estado

    return None


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
    lineas = [line for line in out.splitlines() if any(p in line for p in LEGACY_PATTERNS)]
    return "\n".join(lineas) if lineas else "ninguno"


def gateway_status() -> str:
    hermes = hermes_cli_path()
    if not hermes.exists():
        return f"Hermes CLI no existe: {hermes}"
    code, out = run_cmd([str(hermes), "gateway", "status"], cwd=Path.home(), timeout=30)
    if code != 0:
        return f"ERROR gateway status: {out}"
    return out or "sin salida"


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
        if "status: pending" in texto:
            return str(path)
    return "ninguna"


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
        estado_repo=f"ruta={repo}; status={git_status(repo) if repo.exists() else 'no disponible'}; log={git_log(repo) if repo.exists() else 'no disponible'}; gateway={gateway_status()}",
        estado_gate=leer_gate(repo) if repo.exists() else "no disponible",
        tarea_seleccionada="ninguna",
        evidencia_generada="ninguna",
        errores="; ".join(errores) if errores else "ninguno",
        proximo_paso="corregir errores" if errores else "usar /avanzar o /actualizar",
    )


def comando_actualizar() -> Resultado:
    repo = repo_path()
    if not repo.exists():
        return Resultado("/actualizar", "BLOCKED", f"repo no existe: {repo}", "no disponible", "ninguna", "ninguna", "repo inexistente", "verificar MAPA_RUTAS_REPOS_GCP.md")
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
        return Resultado("/pausar", "BLOCKED", f"repo no existe: {repo}", "no disponible", "ninguna", "ninguna", "repo inexistente", "verificar ruta absoluta")
    path = escribir_estado(repo, "PAUSED", "pausa solicitada por owner desde Telegram/Hermes")
    return Resultado("/pausar", "OK", git_status(repo), leer_gate(repo), "ninguna", str(path), "ninguno", "usar /reanudar para abrir la factoria")


def comando_reanudar() -> Resultado:
    repo = repo_path()
    if not repo.exists():
        return Resultado("/reanudar", "BLOCKED", f"repo no existe: {repo}", "no disponible", "ninguna", "ninguna", "repo inexistente", "verificar ruta absoluta")

    audit = audit_gate_status(repo)
    if audit in {"WAITING_AUDIT", "BLOCKED", "HOLD"}:
        return Resultado("/reanudar", "BLOCKED", git_status(repo), leer_gate(repo), "ninguna", "ninguna", f"gate bloqueante: {audit}", "auditar o desbloquear gate")

    path = escribir_estado(repo, "OPEN", "reanudar solicitada por owner desde Telegram/Hermes")
    return Resultado("/reanudar", "OK", git_status(repo), leer_gate(repo), "ninguna", str(path), "ninguno", "usar /avanzar para ejecutar un ciclo")


def comando_avanzar() -> Resultado:
    repo = repo_path()
    if not repo.exists():
        return Resultado("/avanzar", "BLOCKED", f"repo no existe: {repo}", "no disponible", "ninguna", "ninguna", "repo inexistente", "verificar MAPA_RUTAS_REPOS_GCP.md")

    ok, pull_out = git_pull(repo)
    if not ok:
        return Resultado("/avanzar", "BLOCKED", pull_out, leer_gate(repo), "ninguna", "ninguna", "fallo git pull --ff-only origin main", "resolver conflicto de git")

    legacy = procesos_legacy()
    if legacy != "ninguno":
        return Resultado("/avanzar", "BLOCKED", pull_out, leer_gate(repo), "ninguna", "ninguna", f"procesos legacy activos: {legacy}", "detener contaminacion legacy")

    bloqueante = estado_bloqueante_actual(repo)
    if bloqueante:
        return Resultado("/avanzar", "BLOCKED", pull_out, leer_gate(repo), "ninguna", "ninguna", f"gate bloqueante: {bloqueante}", "usar /auditar, /reanudar o resolver bloqueo")

    task = seleccionar_task_pending(repo)
    if task == "ninguna" or task.startswith("ninguna:"):
        return Resultado("/avanzar", "BLOCKED", pull_out, leer_gate(repo), task, "ninguna", "no hay TaskSpec pending", "crear una TaskSpec pending")

    evidencia_dir = repo / "factory/evidence" / Path(task).stem
    evidencia_dir.mkdir(parents=True, exist_ok=True)
    (evidencia_dir / "control_preflight.txt").write_text(
        f"comando=/avanzar\nfecha={ahora_iso()}\nrepo={repo}\ntask={task}\ngate={leer_gate(repo)}\npull={pull_out}\n",
        encoding="utf-8",
    )
    escribir_estado(repo, "WAITING_AUDIT", f"ciclo preparado para {Path(task).name}; requiere ejecucion/auditoria de Hermes")

    return Resultado(
        "/avanzar",
        "OK",
        pull_out,
        leer_gate(repo),
        task,
        str(evidencia_dir),
        "ninguno",
        "Hermes debe ejecutar la TaskSpec seleccionada y luego /auditar",
    )


def comando_auditar() -> Resultado:
    repo = repo_path()
    if not repo.exists():
        return Resultado("/auditar", "BLOCKED", f"repo no existe: {repo}", "no disponible", "ninguna", "ninguna", "repo inexistente", "verificar ruta absoluta")
    evidence = repo / "factory/evidence"
    recientes = []
    if evidence.exists():
        recientes = [str(p) for p in sorted(evidence.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True)[:5]]
    decision = "NO_VALIDADO" if not recientes else "BLOCKED"
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
    parser.add_argument("comando", choices=["estado", "actualizar", "pausar", "reanudar", "avanzar", "auditar"])
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
