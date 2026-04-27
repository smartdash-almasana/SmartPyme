from __future__ import annotations

from pathlib import Path
from typing import Any

from factory.orchestrator.agent_runner import MockAgentRunner
from factory.orchestrator.evidence_store import EvidenceStore
from factory.orchestrator.hallazgo_store import HallazgoStore


def run_one_cycle(repo_root: str | Path, agent_runner: Any | None = None) -> dict[str, Any]:
    """Run one deterministic Hermes orchestration cycle.

    This function deliberately uses a mock runner by default. It does not call
    Vertex, Gemini, Codex, Hermes Agent, network APIs, or continuous workers.
    """
    root = Path(repo_root)
    store = HallazgoStore(root)
    evidence = EvidenceStore(root)
    runner = agent_runner or MockAgentRunner()

    pending = store.list_pending()
    if not pending:
        return {"status": "idle"}

    original = pending[0]
    hallazgo_id = original.stem
    in_progress = store.move_to_in_progress(original)
    hallazgo_text = store.read_hallazgo(in_progress)

    try:
        builder_result = runner.run_builder(hallazgo_text)
        evidence.write_builder_report(hallazgo_id, builder_result.content)

        if builder_result.status != "submitted":
            blocked = store.move_to_blocked(in_progress, reason="BUILDER_NOT_SUBMITTED")
            evidence.write_status(
                hallazgo_id,
                {
                    "hallazgo_id": hallazgo_id,
                    "status": "blocked",
                    "final_state": "blocked",
                    "builder_verdict": builder_result.status,
                    "auditor_verdict": None,
                    "files_touched": [],
                    "commit": None,
                },
            )
            return _result("blocked", hallazgo_id, blocked, evidence)

        auditor_result = runner.run_auditor(hallazgo_text, builder_result.content)
        evidence.write_auditor_report(hallazgo_id, auditor_result.content)
        auditor_verdict = auditor_result.data.get("verdict")

        if auditor_verdict == "VALIDADO":
            done = store.move_to_done(in_progress)
            evidence.write_status(
                hallazgo_id,
                {
                    "hallazgo_id": hallazgo_id,
                    "status": "done",
                    "final_state": "done",
                    "builder_verdict": builder_result.status,
                    "auditor_verdict": auditor_verdict,
                    "files_touched": [],
                    "commit": None,
                },
            )
            return _result("done", hallazgo_id, done, evidence)

        blocked = store.move_to_blocked(in_progress, reason=f"AUDITOR_VERDICT_{auditor_verdict}")
        evidence.write_status(
            hallazgo_id,
            {
                "hallazgo_id": hallazgo_id,
                "status": "blocked",
                "final_state": "blocked",
                "builder_verdict": builder_result.status,
                "auditor_verdict": auditor_verdict,
                "files_touched": [],
                "commit": None,
            },
        )
        return _result("blocked", hallazgo_id, blocked, evidence)

    except Exception as exc:
        blocked = store.move_to_blocked(in_progress, reason=f"EXCEPTION: {exc}")
        evidence.write_text(hallazgo_id, "error.txt", str(exc))
        evidence.write_status(
            hallazgo_id,
            {
                "hallazgo_id": hallazgo_id,
                "status": "blocked",
                "final_state": "blocked",
                "builder_verdict": None,
                "auditor_verdict": None,
                "files_touched": [],
                "commit": None,
            },
        )
        return _result("blocked", hallazgo_id, blocked, evidence)


def _result(status: str, hallazgo_id: str, final_path: Path, evidence: EvidenceStore) -> dict[str, Any]:
    return {
        "status": status,
        "hallazgo_id": hallazgo_id,
        "final_state": status,
        "final_path": str(final_path),
        "evidence_dir": str(evidence.evidence_dir(hallazgo_id)),
    }
