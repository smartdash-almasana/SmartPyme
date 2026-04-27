from datetime import datetime, timezone
from pathlib import Path
import subprocess
import sys
import re

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from factory.telegram_notify import notify_cycle_result

TASKS_DIR = REPO / "factory" / "ai_governance" / "tasks"
TEMPLATE_TASK = REPO / "factory/tasks/template_codex_task.yaml"
CODEX_RUNNER = REPO / "scripts/codex_builder_runner.py"
POST_CYCLE = REPO / "scripts/factory_post_cycle_control.py"
CONTROL = REPO / "factory" / "control"
GATE = CONTROL / "AUDIT_GATE.md"
STATUS = CONTROL / "FACTORY_STATUS.md"


def notify(status, detail=""):
    try:
        notify_cycle_result(status, detail)
    except Exception as exc:
        print(f"NOTIFY_ERROR {type(exc).__name__}: {exc}")


def ts():
    return datetime.now(timezone.utc).isoformat()


def gate_status():
    if not GATE.exists():
        return "APPROVED"
    text = GATE.read_text(encoding="utf-8", errors="replace")
    for line in text.splitlines():
        if line.startswith("status:"):
            return line.split(":", 1)[1].strip().upper()
    return "UNKNOWN"


def write_status(result, detail=""):
    CONTROL.mkdir(parents=True, exist_ok=True)
    STATUS.write_text(
        f"# FACTORY STATUS\n\nupdated_at: {ts()}\nlast_cycle_result: {result}\naudit_gate: {gate_status()}\nlast_error: {detail or 'none'}\n",
        encoding="utf-8",
    )


def set_gate(status, code=0):
    CONTROL.mkdir(parents=True, exist_ok=True)
    GATE.write_text(
        f"# AUDIT GATE\n\nstatus: {status}\nupdated_at: {ts()}\nlast_returncode: {code}\n",
        encoding="utf-8",
    )


def post_cycle(code):
    if not POST_CYCLE.exists():
        print("POST_CYCLE_MISSING")
        notify("POST_CYCLE_MISSING", str(POST_CYCLE))
        return code
    r = subprocess.run(["python3", str(POST_CYCLE), "--repo", str(REPO), "--codex-returncode", str(code)])
    if r.returncode:
        notify("INCONSISTENCY_DETECTED", f"post_cycle_returncode={r.returncode}; codex_returncode={code}")
    return r.returncode if r.returncode else code


def task_is_pending(path):
    text = path.read_text(encoding="utf-8", errors="replace").lower()
    return "task_id:" in text and "status: pending" in text


def select_task():
    if TASKS_DIR.exists():
        pending = sorted(p for p in TASKS_DIR.glob("*.yaml") if task_is_pending(p))
        if pending:
            for p in pending:
                if p.name == "core_reconciliacion_v1.yaml":
                    return p
            return pending[0]
    return TEMPLATE_TASK if TEMPLATE_TASK.exists() else None


def mark_task_done(rel_task):
    try:
        tp = (REPO / rel_task).resolve()
        txt = tp.read_text()
        txt = re.sub(r"status:\\s*pending", "status: done", txt)
        tp.write_text(txt)
        notify("TASK_DONE", str(rel_task))
    except Exception as e:
        notify("TASK_DONE_ERROR", str(e))


def main():
    notify("CYCLE_START", f"repo={REPO}")

    current_gate = gate_status()
    if current_gate == "WAITING_AUDIT":
        print("AUDIT_GATE_OBSERVED_CONTINUING")
        write_status("AUDIT_GATE_OBSERVED_CONTINUING", "continuous mode")
        notify("AUDIT_BLOCKED", "gate=WAITING_AUDIT; continuous mode")

    set_gate("RUNNING")
    write_status("RUNNING", "cycle started")

    task = select_task()
    if task:
        rel_task = task.relative_to(REPO)
        print(f"[Hermes->Codex] Dispatching task: {rel_task}")
        notify("TASK_DISPATCH", str(rel_task))
        r = subprocess.run(["python3", str(CODEX_RUNNER), "--repo", str(REPO), "--task", str(rel_task), "--full-auto", "--timeout", "3600"])
        code = post_cycle(r.returncode)
        if code == 0:
            mark_task_done(rel_task)
    else:
        print("[Hermes] No task, post-cycle only.")
        notify("NO_TASK", "Sin tareas pending")
        code = post_cycle(0)

    set_gate("WAITING_AUDIT", code)
    write_status("WAITING_AUDIT", "cycle closed")
    print("CYCLE_CLOSED_WAITING_AUDIT")

    if code == 0:
        notify("CYCLE_OK", "cycle closed; gate=WAITING_AUDIT")
    else:
        notify("CYCLE_FAIL", f"exit_code={code}; gate=WAITING_AUDIT")

    return code


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        notify("CYCLE_INTERRUPTED", "KeyboardInterrupt")
        raise
    except Exception as exc:
        notify("CYCLE_CRASH", f"{type(exc).__name__}: {exc}")
        raise
