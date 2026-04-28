from __future__ import annotations

import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CONTROL = REPO / "factory" / "control"
GATE = CONTROL / "AUDIT_GATE.md"
LOCK = CONTROL / ".telegram_cycle_lock"
RUNNER = REPO / "scripts" / "hermes_factory_runner.py"
LOG = REPO / "factory" / "runner_logs" / "telegram_trigger_cycle.log"


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_log(message: str) -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as fh:
        fh.write(f"{now()} {message}\n")


def run(command: list[str]) -> int:
    write_log("RUN " + " ".join(command))
    result = subprocess.run(
        command,
        cwd=REPO,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.stdout.strip():
        write_log("STDOUT " + result.stdout.strip()[-3000:])
    if result.stderr.strip():
        write_log("STDERR " + result.stderr.strip()[-3000:])
    write_log(f"RETURNCODE {result.returncode}")
    return result.returncode


def write_gate(status: str, reason: str) -> None:
    CONTROL.mkdir(parents=True, exist_ok=True)
    GATE.write_text(
        "# AUDIT GATE\n\n"
        f"status: {status}\n"
        f"updated_at: {now()}\n"
        "updated_by: telegram_trigger_cycle\n"
        f"reason: {reason}\n",
        encoding="utf-8",
    )


def main() -> int:
    CONTROL.mkdir(parents=True, exist_ok=True)
    if LOCK.exists():
        write_log("SKIP lock exists")
        return 0

    LOCK.write_text(now(), encoding="utf-8")
    try:
        write_log("START telegram cycle trigger")

        pull_code = run(["git", "pull", "--ff-only", "--autostash", "origin", "main"])
        if pull_code != 0:
            write_gate("BLOCKED", "git_pull_failed_from_telegram_trigger")
            return pull_code

        write_gate("APPROVED", "telegram_seguir_after_pull")

        if not RUNNER.exists():
            write_gate("BLOCKED", "missing_hermes_factory_runner")
            write_log(f"MISSING {RUNNER}")
            return 1

        return run([sys.executable, str(RUNNER)])
    finally:
        try:
            LOCK.unlink(missing_ok=True)
        except Exception as exc:
            write_log(f"LOCK_CLEANUP_ERROR {type(exc).__name__}: {exc}")
        write_log("END telegram cycle trigger")


if __name__ == "__main__":
    raise SystemExit(main())
