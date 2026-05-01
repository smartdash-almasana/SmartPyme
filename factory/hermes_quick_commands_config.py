"""Configuracion de quick commands Hermes para SmartPyme Factory.

Este modulo no ejecuta la factoria. Solo construye la configuracion local
que Hermes Gateway debe leer en /home/neoalmasana/.hermes/config.yaml.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

REPO_SMARTPYME = Path(
    os.getenv(
        "SMARTPYME_REPO",
        "/home/neoalmasana/smartpyme-factory/repos/SmartPyme",
    )
)
PYTHON = "/usr/bin/python3"
CONTROL_CLI = REPO_SMARTPYME / "factory/hermes_control_cli.py"
COMANDOS = ("estado", "actualizar", "pausar", "reanudar", "avanzar", "auditar")


def comando_control(nombre: str, repo: Path = REPO_SMARTPYME) -> str:
    """Devuelve el comando absoluto para un control de SmartPyme."""
    control_cli = repo / "factory/hermes_control_cli.py"
    return f"{PYTHON} {control_cli} {nombre}"


def quick_commands(repo: Path = REPO_SMARTPYME) -> dict[str, dict[str, str]]:
    """Mapa de quick commands que Hermes debe inyectar en config.yaml."""
    return {
        nombre: {
            "type": "exec",
            "command": comando_control(nombre, repo),
        }
        for nombre in COMANDOS
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
