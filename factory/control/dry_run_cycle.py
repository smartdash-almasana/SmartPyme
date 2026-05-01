"""Deterministic dry-run cycle for SmartPyme Factory v2.1.

No LLM calls, no Telegram calls, no MCP calls. This validates the local control plane.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

from factory.control.circuit_breaker import CircuitBreaker
from factory.control.heartbeat import write_heartbeat
from factory.control.telegram_handler import create_callback_token, mark_update_processed


@dataclass
class DryRunResult:
    task_id: str
    build_status: str
    audit_status: str
    final_state: str
    evidence_path: str
    callback_data_bytes: int


def run_dry_run_cycle(
    task_id: str = "TASK-DRY-RUN", evidence_root: str | Path = "factory/ai_governance/evidence"
) -> dict[str, object]:
    evidence_dir = Path(evidence_root) / task_id
    evidence_dir.mkdir(parents=True, exist_ok=True)

    write_heartbeat(evidence_dir / "heartbeat.json")
    breaker = CircuitBreaker(max_failures_per_hour=10)
    if breaker.is_open():
        final_state = "ESCALATED"
        build_status = "BUILD_BLOCKED"
        audit_status = "AUDIT_BLOCKED"
    else:
        build_status = "BUILD_SUCCESS"
        audit_status = "AUDIT_PASSED"
        final_state = "AWAITING_HUMAN_MERGE"

    db_path = evidence_dir / "telegram_control.db"
    mark_update_processed(1, "/estado", db_path=db_path)
    token = create_callback_token(task_id, "APPROVE", db_path=db_path)

    result = DryRunResult(
        task_id=task_id,
        build_status=build_status,
        audit_status=audit_status,
        final_state=final_state,
        evidence_path=str(evidence_dir),
        callback_data_bytes=len(token.encode("utf-8")),
    )
    (evidence_dir / "dry_run_result.json").write_text(str(asdict(result)), encoding="utf-8")
    (evidence_dir / "completed_at.txt").write_text(
        datetime.now(timezone.utc).isoformat(), encoding="utf-8"
    )
    return asdict(result)


if __name__ == "__main__":
    print(run_dry_run_cycle())
