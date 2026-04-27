from __future__ import annotations

from pathlib import Path

from factory.orchestrator.agent_runner import MockAgentRunner
from factory.orchestrator.hermes_loop import run_one_cycle


def _write_pending(repo_root: Path, name: str = "001-test.md") -> Path:
    pending = repo_root / "factory" / "hallazgos" / "pending"
    pending.mkdir(parents=True, exist_ok=True)
    hallazgo = pending / name
    hallazgo.write_text("# HALLAZGO\n\n## META\n- estado: pending\n", encoding="utf-8")
    return hallazgo


def test_run_one_cycle_idle_when_no_pending(tmp_path: Path):
    result = run_one_cycle(tmp_path)
    assert result == {"status": "idle"}


def test_pending_moves_to_done_when_auditor_validates(tmp_path: Path):
    _write_pending(tmp_path, "001-validado.md")

    result = run_one_cycle(tmp_path, agent_runner=MockAgentRunner(auditor_verdict="VALIDADO"))

    assert result["status"] == "done"
    assert result["final_state"] == "done"
    assert (tmp_path / "factory" / "hallazgos" / "done" / "001-validado.md").exists()
    assert not list((tmp_path / "factory" / "hallazgos" / "pending").glob("*.md"))


def test_evidence_files_are_created(tmp_path: Path):
    _write_pending(tmp_path, "002-evidencia.md")

    result = run_one_cycle(tmp_path)

    evidence_dir = Path(result["evidence_dir"])
    assert (evidence_dir / "builder_report.md").exists()
    assert (evidence_dir / "auditor_report.md").exists()
    assert (evidence_dir / "status.json").exists()


def test_no_pending_files_remain_after_successful_cycle(tmp_path: Path):
    _write_pending(tmp_path, "003-sin-pending.md")

    run_one_cycle(tmp_path)

    pending = tmp_path / "factory" / "hallazgos" / "pending"
    assert list(pending.glob("*.md")) == []


def test_auditor_no_validado_moves_to_blocked(tmp_path: Path):
    _write_pending(tmp_path, "004-bloqueado.md")

    result = run_one_cycle(tmp_path, agent_runner=MockAgentRunner(auditor_verdict="NO_VALIDADO"))

    assert result["status"] == "blocked"
    assert result["final_state"] == "blocked"
    assert (tmp_path / "factory" / "hallazgos" / "blocked" / "004-bloqueado.md").exists()
    assert (tmp_path / "factory" / "evidence" / "004-bloqueado" / "auditor_report.md").exists()
