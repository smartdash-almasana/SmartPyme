#!/usr/bin/env python3
"""Control operativo seguro para SmartPyme Factory vía Hermes.

Este archivo NO es un bot paralelo.
Es una herramienta invocable por Hermes Gateway para ejecutar comandos de control
acotados: estado, actualizar, pausar, reanudar, avanzar y auditar.

`/avanzar` ejecuta una única TaskSpec declarativa del repo: comandos preflight,
tests requeridos y post comandos, con evidencia reproducible. No reactiva runners
legacy ni reemplaza a Hermes.
"""

from __future__ import annotations

import argparse
import fnmatch
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
TASK_LIST_FIELDS = (
    "allowed_files",
    "forbidden_files",
    "locked_files",
    "required_tests",
    "acceptance_criteria",
    "preflight_commands",
    "post_commands",
)


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


@dataclass
class TaskSpecMinima:
    path: Path
    task_id: str
    mode: str
    status: str
    allowed_files: list[str]
    forbidden_files: list[str]
    required_tests: list[str]
    preflight_commands: list[str]
    post_commands: list[str]
    acceptance_criteria: list[str]


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


def run_shell(command: str, cwd: Path, timeout: int = 180) -> tuple[int, str]:
    try:
        proc = subprocess.run(
            command,
            cwd=str(cwd),
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
            shell=True,
            executable="/bin/bash",
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
    """Extrae un estado actual desde una línea exacta tipo `status:` o `estado:`."""
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


def git_status_paths(repo: Path) -> list[str]:
    status = git_status(repo)
    if status == "limpio" or status.startswith("ERROR"):
        return []
    paths: list[str] = []
    for line in status.splitlines():
        if len(line) >= 4:
            paths.append(line[3:].strip())
    return paths


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


def _scalar(texto: str, campo: str) -> str:
    prefijo = f"{campo}:"
    for linea in texto.splitlines():
        limpia = linea.strip()
        if limpia.startswith(prefijo):
            return limpia.split(":", 1)[1].strip().strip('"')
    return ""


def _lista(texto: str, campo: str) -> list[str]:
    lineas = texto.splitlines()
    items: list[str] = []
    dentro = False
    for linea in lineas:
        limpia = linea.strip()
        if limpia == f"{campo}:":
            dentro = True
            continue
        if dentro:
            if not linea.startswith((" ", "\t")) and limpia:
                break
            if limpia.startswith("- "):
                items.append(limpia[2:].strip().strip('"'))
    return items


def cargar_taskspec(path: Path) -> TaskSpecMinima:
    texto = leer_texto(path)
    return TaskSpecMinima(
        path=path,
        task_id=_scalar(texto, "task_id") or path.stem,
        mode=_scalar(texto, "mode"),
        status=_scalar(texto, "status"),
        allowed_files=_lista(texto, "allowed_files"),
        forbidden_files=_lista(texto, "forbidden_files"),
        required_tests=_lista(texto, "required_tests"),
        preflight_commands=_lista(texto, "preflight_commands"),
        post_commands=_lista(texto, "post_commands"),
        acceptance_criteria=_lista(texto, "acceptance_criteria"),
    )


def validar_taskspec_minima(task: TaskSpecMinima) -> list[str]:
    errores: list[str] = []
    if task.status != "pending":
        errores.append(f"status invalido para dispatch: {task.status}")
    if task.mode not in {"create_only", "patch_only", "governance", "product"}:
        errores.append(f"mode invalido: {task.mode}")
    if not task.allowed_files:
        errores.append("allowed_files vacio")
    if not task.required_tests:
        errores.append("required_tests vacio")
    if not task.acceptance_criteria:
        errores.append("acceptance_criteria vacio")
    return errores


def ejecutar_bloque(nombre: str, comandos: list[str], repo: Path, evidencia_dir: Path) -> tuple[bool, str]:
    salida: list[str] = []
    ok = True
    for index, command in enumerate(comandos, start=1):
        code, out = run_shell(command, cwd=repo)
        salida.append(f"$ {command}\nEXIT_CODE={code}\n{out}\n")
        if code != 0:
            ok = False
            break
    texto = "\n".join(salida) if salida else "sin comandos\n"
    (evidencia_dir / f"{nombre}.txt").write_text(texto, encoding="utf-8")
    return ok, texto


def _match_any(path: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatch(path, pattern) for pattern in patterns)


def validar_alcance_git(repo: Path, task: TaskSpecMinima) -> list[str]:
    violaciones: list[str] = []
    for path in git_status_paths(repo):
        if path.startswith("factory/evidence/") or path == "factory/control/FACTORY_STATUS.md":
            continue
        if _match_any(path, task.forbidden_files):
            violaciones.append(f"archivo prohibido modificado: {path}")
        elif not _match_any(path, task.allowed_files):
            violaciones.append(f"archivo fuera de allowed_files: {path}")
    return violaciones


def ejecutar_taskspec(repo: Path, task_path: Path, pull_out: str) -> tuple[str, Path, str]:
    task = cargar_taskspec(task_path)
    evidencia_dir = repo / "factory/evidence" / task.task_id
    evidencia_dir.mkdir(parents=True, exist_ok=True)

    (evidencia_dir / "task.yaml").write_text(leer_texto(task_path), encoding="utf-8")
    (evidencia_dir / "cycle.md").write_text(
        f"# Ciclo Hermes\n\nfecha: {ahora_iso()}\nrepo: {repo}\ntask: {task_path}\npull:\n{pull_out}\n",
        encoding="utf-8",
    )

    errores = validar_taskspec_minima(task)
    if errores:
        (evidencia_dir / "decision.txt").write_text("BLOCKED\n" + "\n".join(errores), encoding="utf-8")
        escribir_estado(repo, "BLOCKED", f"TaskSpec invalida: {task.task_id}")
        return "BLOCKED", evidencia_dir, "; ".join(errores)

    comandos_txt = [
        "# preflight_commands",
        *task.preflight_commands,
        "# required_tests",
        *task.required_tests,
        "# post_commands",
        *task.post_commands,
    ]
    (evidencia_dir / "commands.txt").write_text("\n".join(comandos_txt) + "\n", encoding="utf-8")

    preflight_ok, _ = ejecutar_bloque("preflight", task.preflight_commands, repo, evidencia_dir)
    if not preflight_ok:
        (evidencia_dir / "decision.txt").write_text("BLOCKED\npreflight fallo\n", encoding="utf-8")
        escribir_estado(repo, "BLOCKED", f"preflight fallo para {task.task_id}")
        return "BLOCKED", evidencia_dir, "preflight fallo"

    tests_ok, _ = ejecutar_bloque("tests", task.required_tests, repo, evidencia_dir)
    post_ok, _ = ejecutar_bloque("post", task.post_commands, repo, evidencia_dir)

    status = git_status(repo)
    (evidencia_dir / "git_status.txt").write_text(status + "\n", encoding="utf-8")
    code, diff = run_cmd(["git", "diff"], cwd=repo, timeout=120)
    (evidencia_dir / "git_diff.patch").write_text(diff + "\n", encoding="utf-8")

    violaciones = validar_alcance_git(repo, task)
    if violaciones:
        (evidencia_dir / "decision.txt").write_text("REJECTED\n" + "\n".join(violaciones), encoding="utf-8")
        escribir_estado(repo, "WAITING_AUDIT", f"ciclo con violaciones de alcance: {task.task_id}")
        return "REJECTED", evidencia_dir, "; ".join(violaciones)

    if not tests_ok:
        (evidencia_dir / "decision.txt").write_text("BLOCKED\nrequired_tests fallo\n", encoding="utf-8")
        escribir_estado(repo, "WAITING_AUDIT", f"tests fallidos para {task.task_id}")
        return "BLOCKED", evidencia_dir, "required_tests fallo"

    if not post_ok:
        (evidencia_dir / "decision.txt").write_text("BLOCKED\npost_commands fallo\n", encoding="utf-8")
        escribir_estado(repo, "WAITING_AUDIT", f"post_commands fallaron para {task.task_id}")
        return "BLOCKED", evidencia_dir, "post_commands fallo"

    (evidencia_dir / "decision.txt").write_text("SUBMITTED\nrequiere auditoria humana\n", encoding="utf-8")
    escribir_estado(repo, "WAITING_AUDIT", f"ciclo ejecutado para {task.task_id}; requiere auditoria")
    return "OK", evidencia_dir, "ninguno"


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

    decision, evidencia_dir, errores = ejecutar_taskspec(repo, Path(task), pull_out)
    return Resultado(
        "/avanzar",
        decision,
        git_status(repo),
        leer_gate(repo),
        task,
        str(evidencia_dir),
        errores,
        "usar /auditar" if decision == "OK" else "revisar evidencia y corregir bloqueo",
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
