from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import factory.core.run_taskloop_once as taskloop_cli


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
    assert "check-remote-sync" in result.stdout


def test_cli_with_closed_gate_blocks(tmp_path):
    """CLI con gate cerrado debe retornar status blocked."""
    tasks_dir = tmp_path / "taskspecs"
    evidence_dir = tmp_path / "evidence"
    gate_path = tmp_path / "AUDIT_GATE.md"
    _closed_gate(gate_path)

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
    assert data.get("blocking_reason") == "AUDIT_GATE_CLOSED"
    assert data.get("gate_status") == "CLOSED"


def test_cli_calls_sovereign_mode(tmp_path):
    """Verificar que CLI funciona y produce JSON válido."""
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
    assert "status" in data
    assert data["status"] in {"idle", "blocked"}
    if data.get("blocking_reason"):
        assert isinstance(data["blocking_reason"], str)


def test_check_remote_sync_passes_when_origin_matches_head(monkeypatch, tmp_path):
    """La verificación remota pasa solo si worktree limpio y origin/<branch> coincide."""
    head = "a" * 40

    def fake_run_git(repo_root: Path, args: list[str]):
        if args == ["status", "--short"]:
            return 0, "", ""
        if args == ["branch", "--show-current"]:
            return 0, "factory/test", ""
        if args == ["rev-parse", "HEAD"]:
            return 0, head, ""
        if args == ["ls-remote", "origin", "refs/heads/factory/test"]:
            return 0, f"{head}\trefs/heads/factory/test", ""
        raise AssertionError(args)

    monkeypatch.setattr(taskloop_cli, "_run_git", fake_run_git)

    result = taskloop_cli.check_remote_sync(tmp_path)

    assert result["remote_sync_status"] == "DONE_REMOTE_SYNCED"
    assert result["remote_sync_ok"] is True
    assert result["local_head"] == head
    assert result["remote_head"] == head


def test_check_remote_sync_blocks_dirty_worktree(monkeypatch, tmp_path):
    """Si hay cambios locales, no existe DONE remoto aunque haya ejecución exitosa."""

    def fake_run_git(repo_root: Path, args: list[str]):
        if args == ["status", "--short"]:
            return 0, " M factory/control/AUDIT_GATE.md", ""
        raise AssertionError(args)

    monkeypatch.setattr(taskloop_cli, "_run_git", fake_run_git)

    result = taskloop_cli.check_remote_sync(tmp_path)

    assert result["remote_sync_status"] == "BLOCKED_REMOTE_SYNC"
    assert result["remote_sync_ok"] is False
    assert result["remote_sync_reason"] == "DIRTY_WORKTREE"
    assert "factory/control/AUDIT_GATE.md" in result["git_status"]


def test_check_remote_sync_blocks_remote_mismatch(monkeypatch, tmp_path):
    """Si origin/<branch> no apunta al HEAD local, el hito no está cerrado."""
    local_head = "a" * 40
    remote_head = "b" * 40

    def fake_run_git(repo_root: Path, args: list[str]):
        if args == ["status", "--short"]:
            return 0, "", ""
        if args == ["branch", "--show-current"]:
            return 0, "factory/test", ""
        if args == ["rev-parse", "HEAD"]:
            return 0, local_head, ""
        if args == ["ls-remote", "origin", "refs/heads/factory/test"]:
            return 0, f"{remote_head}\trefs/heads/factory/test", ""
        raise AssertionError(args)

    monkeypatch.setattr(taskloop_cli, "_run_git", fake_run_git)

    result = taskloop_cli.check_remote_sync(tmp_path)

    assert result["remote_sync_status"] == "BLOCKED_REMOTE_SYNC"
    assert result["remote_sync_ok"] is False
    assert result["remote_sync_reason"] == "REMOTE_HEAD_MISMATCH"
    assert result["local_head"] == local_head
    assert result["remote_head"] == remote_head
