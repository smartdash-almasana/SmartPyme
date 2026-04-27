from datetime import datetime, timezone
from pathlib import Path
import subprocess
import sys

REPO = Path(__file__).resolve().parents[1]
TASKS_DIR = REPO / "factory" / "ai_governance" / "tasks"
TEMPLATE_TASK = REPO / "factory/tasks/template_codex_task.yaml"
CODEX_RUNNER = REPO / "scripts/codex_builder_runner.py"
POST_CYCLE = REPO / "scripts/factory_post_cycle_control.py"
CONTROL = REPO / "factory" / "control"
GATE = CONTROL / "AUDIT_GATE.md"
STATUS = CONTROL / "FACTORY_STATUS.md"


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
        return code
    r = subprocess.run(["python3", str(POST_CYCLE), "--repo", str(REPO), "--codex-returncode", str(code)])
    return r.returncode if r.returncode else code


if gate_status() == "WAITING_AUDIT":
    print("AUDIT_GATE_OBSERVED_CONTINUING")
    write_status("AUDIT_GATE_OBSERVED_CONTINUING", "continuous mode")

set_gate("RUNNING")
write_status("RUNNING", "cycle started")

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

task = select_task()
if task:
    rel_task = task.relative_to(REPO)
    print(f"[Hermes→Codex] Dispatching task: {rel_task}")
    r = subprocess.run(["python3", str(CODEX_RUNNER), "--repo", str(REPO), "--task", str(rel_task), "--full-auto", "--timeout", "3600"])
    code = post_cycle(r.returncode)
else:
    print("[Hermes] No task, post-cycle only.")
    code = post_cycle(0)

set_gate("WAITING_AUDIT", code)
write_status("WAITING_AUDIT", "cycle closed")
print("CYCLE_CLOSED_WAITING_AUDIT")
sys.exit(code)
