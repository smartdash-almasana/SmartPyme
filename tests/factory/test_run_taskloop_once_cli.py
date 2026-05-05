from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def _open_gate(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("# AUDIT GATE\n\nstatus: OPEN\n", encoding="utf-8")


def _closed_gate(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("# AUDIT GATE\n\nstatus: CLOSED\n", encoding="utf-8")


def test_cli_module_compiles():
    """Verificar que el módulo puede ser importado."""
    import factory.core.run_taskloop_once  # noqa: F401


def test_cli_help():
    """Verificar que --help funciona."""
    result = subprocess.run(
        [sys.executable, "-m", "factory.core.run_taskloop_once", "--help"],
        capture_output=True,
        text=True,
        cwd=".",
    )
    assert result.returncode == 0
    assert "usage:" in result.stdout.lower()
    assert "sovereign" in result.stdout


def test_cli_with_closed_gate_blocks(tmp_path):
    """CLI con gate cerrado debe retornar status blocked."""
    tasks_dir = tmp_path / "taskspecs"
    evidence_dir = tmp_path / "evidence"
    gate_path = tmp_path / "AUDIT_GATE.md"
    _closed_gate(gate_path)

    # Crear estructura mínima de taskspecs para que el store no falle
    (tasks_dir / "pending").mkdir(parents=True, exist_ok=True)

    cmd = [
        sys.executable,
        "-m",
        "factory.core.run_taskloop_once",
        "--mode",
        "sovereign",
        "--tasks-dir",
        str(tasks_dir),
        "--evidence-dir",
        str(evidence_dir),
        "--gate-path",
        str(gate_path),
        "--repo-root",
        str(tmp_path),
        "--compact",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=".")
    assert result.returncode == 0, f"stderr: {result.stderr}"

    data = json.loads(result.stdout)
    assert data["status"] == "blocked"
    assert data.get("reason") == "AUDIT_GATE_CLOSED" or data.get("blocking_reason") == "AUDIT_GATE_CLOSED"
    assert data.get("gate_status") == "CLOSED"


def test_cli_calls_sovereign_mode(tmp_path):
    """Verificar que CLI funciona y produce JSON válido."""
    # Crear gate abierto y estructura vacía
    gate_path = tmp_path / "AUDIT_GATE.md"
    _open_gate(gate_path)
    (tmp_path / "tasks" / "pending").mkdir(parents=True, exist_ok=True)
    (tmp_path / "evidence").mkdir(parents=True, exist_ok=True)

    cmd = [
        sys.executable,
        "-m",
        "factory.core.run_taskloop_once",
        "--mode",
        "sovereign",
        "--tasks-dir",
        str(tmp_path / "tasks"),
        "--evidence-dir",
        str(tmp_path / "evidence"),
        "--gate-path",
        str(gate_path),
        "--repo-root",
        str(tmp_path),
        "--compact",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=".")
    assert result.returncode == 0, f"stderr: {result.stderr}"
    
    data = json.loads(result.stdout)
    # Sin tasks pendientes, debería retornar idle o blocked
    assert "status" in data
    assert data["status"] in {"idle", "blocked"}
    if data.get("blocking_reason"):
        assert isinstance(data["blocking_reason"], str)