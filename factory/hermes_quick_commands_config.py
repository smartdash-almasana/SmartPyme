"""Configuracion oficial de quick commands Hermes para SmartPyme Factory.

Fuente oficial Hermes:
- ~/.hermes/config.yaml acepta `quick_commands`.
- Cada quick command puede ser `type: exec` con `command`.
- Funciona desde Telegram y otras plataformas del Gateway.

Este modulo no ejecuta la factoria. Solo construye la configuracion local
que Hermes Gateway debe leer.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


REPO_SMARTPYME = Path("/opt/smartpyme-factory/repos/SmartPyme")
PYTHON = "python3"
CONTROL_CLI = "factory/hermes_control_cli.py"


def comando_control(nombre: str, repo: Path = REPO_SMARTPYME) -> str:
    """Devuelve el comando shell absoluto para un control de SmartPyme."""
    return f"cd {repo} && {PYTHON} {CONTROL_CLI} {nombre}"


def quick_commands(repo: Path = REPO_SMARTPYME) -> dict[str, dict[str, str]]:
    """Mapa de quick commands que Hermes debe inyectar en config.yaml."""
    return {
        "estado": {
            "type": "exec",
            "command": comando_control("estado", repo),
        },
        "actualizar": {
            "type": "exec",
            "command": comando_control("actualizar", repo),
        },
        "pausar": {
            "type": "exec",
            "command": comando_control("pausar", repo),
        },
        "reanudar": {
            "type": "exec",
            "command": comando_control("reanudar", repo),
        },
        "avanzar": {
            "type": "exec",
            "command": comando_control("avanzar", repo),
        },
        "auditar": {
            "type": "exec",
            "command": comando_control("auditar", repo),
        },
    }


def aplicar_quick_commands(config: dict[str, Any], repo: Path = REPO_SMARTPYME) -> dict[str, Any]:
    """Devuelve una copia de config.yaml con comandos SmartPyme agregados.

    No elimina configuracion existente. Solo agrega o reemplaza las claves:
    estado, actualizar, pausar, reanudar, avanzar, auditar.
    """
    nuevo = dict(config or {})
    existentes = nuevo.get("quick_commands")
    if not isinstance(existentes, dict):
        existentes = {}
    existentes = dict(existentes)
    existentes.update(quick_commands(repo))
    nuevo["quick_commands"] = existentes

    terminal = nuevo.get("terminal")
    if not isinstance(terminal, dict):
        terminal = {}
    terminal = dict(terminal)
    terminal["cwd"] = str(repo)
    nuevo["terminal"] = terminal
    return nuevo


def comandos_esperados(repo: Path = REPO_SMARTPYME) -> list[str]:
    """Lista textual de comandos esperados para validacion humana o tests."""
    return [v["command"] for v in quick_commands(repo).values()]
