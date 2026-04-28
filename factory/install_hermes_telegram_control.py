#!/usr/bin/env python3
"""Instala comandos rapidos de Hermes para controlar SmartPyme por Telegram.

Este instalador modifica SOLO el archivo local de Hermes:
/home/neoalmasana/.hermes/config.yaml

No toca tokens. No modifica el core. No crea runners. No crea bots paralelos.
Solo registra quick_commands oficiales de Hermes que invocan factory/hermes_control_cli.py.
"""

from __future__ import annotations

import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except Exception as exc:  # pragma: no cover - error operativo claro
    raise SystemExit(f"ERROR: PyYAML no disponible: {exc}")


REPO = Path("/opt/smartpyme-factory/repos/SmartPyme")
HERMES_CONFIG = Path("/home/neoalmasana/.hermes/config.yaml")
CONTROL_CLI = REPO / "factory/hermes_control_cli.py"
PYTHON = "/usr/bin/python3"

COMANDOS = {
    "estado": "estado",
    "actualizar": "actualizar",
    "pausar": "pausar",
    "reanudar": "reanudar",
    "avanzar": "avanzar",
    "auditar": "auditar",
}


def backup(path: Path) -> Path | None:
    if not path.exists():
        return None
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    target = path.with_name(f"{path.name}.bak.{stamp}")
    shutil.copy2(path, target)
    return target


def load_config(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8", errors="replace"))
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise SystemExit(f"ERROR: config.yaml no es un mapping YAML valido: {path}")
    return data


def command_for(nombre: str) -> str:
    return f"{PYTHON} {CONTROL_CLI} {nombre}"


def install() -> int:
    if not REPO.exists():
        raise SystemExit(f"ERROR: no existe repo SmartPyme: {REPO}")
    if not CONTROL_CLI.exists():
        raise SystemExit(f"ERROR: no existe control CLI: {CONTROL_CLI}")

    HERMES_CONFIG.parent.mkdir(parents=True, exist_ok=True)
    backup_path = backup(HERMES_CONFIG)
    config = load_config(HERMES_CONFIG)

    quick = config.get("quick_commands")
    if quick is None:
        quick = {}
    if not isinstance(quick, dict):
        raise SystemExit("ERROR: quick_commands existe pero no es un mapping YAML")

    for alias, comando in COMANDOS.items():
        quick[alias] = {
            "type": "exec",
            "command": command_for(comando),
        }

    config["quick_commands"] = quick

    HERMES_CONFIG.write_text(
        yaml.safe_dump(config, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )

    print("INSTALACION_OK")
    print(f"config: {HERMES_CONFIG}")
    if backup_path:
        print(f"backup: {backup_path}")
    print("comandos:")
    for alias in COMANDOS:
        print(f"  /{alias} -> {quick[alias]['command']}")
    print("reiniciar_gateway: cd /home/neoalmasana && /home/neoalmasana/.hermes/venv/bin/hermes gateway run --replace")
    return 0


if __name__ == "__main__":
    raise SystemExit(install())
