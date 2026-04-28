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

GATE_ALLOWED_TO_RUN = {"APPROVED", "OPEN", "RUN"}
GATE_BLOCKING = {"WAITING_AUDIT", "BLOCKED", "HOLD"}


def notify(status, detail=""):
    try:
        notify_cycle_result(status, detail)
    except Exception as exc:
        print(f"NOTIFY_ERROR {type(exc).__name__}: {exc}")


def run_git(args, check=False):
    return subprocess.run(["git", *args], cwd=REPO, text=True, capture_output=True, check=check)


def ts():
    return datetime.now(timezone.utc).isoformat()


def read_gate_text():
    if not GATE.exists():
        return ""
    return GATE.read_text(encoding="utf-8", errors="replace")


def gate_field(name, default=""):
    prefix = f"{name}:"
    for line in read_gate_text().splitlines():
        if line.startswith(prefix):
            return line.split(":", 1)[1].strip()
    return default


def gate_status():
    return gate_field("status", "APPROVED").upper()


def write_status(result, detail=""):
    CONTROL.mkdir(parents=True, exist_ok=True)
    STATUS.write_text(
        f"# FACTORY STATUS\n\nupdated_at: {ts()}\nlast_cycle_result: {result}\naudit_gate: {gate_status()}\nlast_error: {detail or 'none'}\n",
        encoding="utf-8",
    )


def set_gate(status, code=0, task=""):
    CONTROL.mkdir(parents=True, exist_ok=True)
    GATE.write_text(
        f"# AUDIT GATE\n\nstatus: {status}\nupdated_at: {ts()}\nlast_returncode: {code}\nlast_task: {task or gate_field('last_task', 'none')}\n",
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
            return pending[0]
    return TEMPLATE_TASK if TEMPLATE_TASK.exists() else None


def replace_task_status(rel_task, new_status):
    tp = (REPO / rel_task).resolve()
    txt = tp.read_text(encoding="utf-8", errors="replace")
    txt = re.sub(r"status:\s*(pending|done|rejected|blocked|in_progress)", f"status: {new_status}", txt, count=1, flags=re.IGNORECASE)
    tp.write_text(txt, encoding="utf-8")


def mark_task_done(rel_task):
    try:
        replace_task_status(rel_task, "done")
        notify("TASK_DONE", str(rel_task))
    except Exception as e:
        notify("TASK_DONE_ERROR", str(e))


def reopen_last_task():
    last_task = gate_field("last_task", "").strip()
    if not last_task or last_task == "none":
        notify("AUDIT_REJECTED_NO_TASK", "last_task missing")
        set_gate("BLOCKED", 1, "none")
        return 1
    try:
        replace_task_status(last_task, "pending")
        notify("AUDIT_REJECTED_REOPENED", last_task)
        set_gate("APPROVED", 0, last_task)
        return 0
    except Exception as exc:
        notify("AUDIT_REJECTED_ERROR", f"{last_task}: {exc}")
        set_gate("BLOCKED", 1, last_task)
        return 1


def enforce_gate_before_dispatch():
    current_gate = gate_status()

    if current_gate in GATE_ALLOWED_TO_RUN:
        return 0

    if current_gate == "REJECTED":
        return reopen_last_task()

    if current_gate in GATE_BLOCKING:
        print(f"AUDIT_GATE_BLOCKING status={current_gate}")
        write_status("AUDIT_GATE_BLOCKING", f"gate={current_gate}")
        notify("AUDIT_BLOCKED", f"gate={current_gate}; no dispatch")
        return 2

    print(f"AUDIT_GATE_UNKNOWN status={current_gate}")
    write_status("AUDIT_GATE_UNKNOWN", f"gate={current_gate}")
    notify("AUDIT_GATE_UNKNOWN", current_gate)
    return 2


def git_has_changes():
    r = run_git(["status", "--porcelain"])
    return bool(r.stdout.strip())


def auto_commit_and_push(rel_task, code):
    if code != 0:
        notify("AUTO_COMMIT_SKIPPED", f"cycle failed; exit_code={code}")
        return
    if not git_has_changes():
        notify("AUTO_COMMIT_SKIPPED", "no worktree changes")
        return

    task_label = str(rel_task) if rel_task else "no-task"
    run_git(["add", "-A"], check=True)
    commit_msg = f"Factory cycle: {task_label}"
    commit = run_git(["commit", "-m", commit_msg])
    if commit.returncode != 0:
        notify("AUTO_COMMIT_FAILED", commit.stderr[-1200:] or commit.stdout[-1200:])
        return

    sha = run_git(["rev-parse", "--short", "HEAD"], check=True).stdout.strip()
    push = run_git(["push", "origin", "main"])
    if push.returncode != 0:
        notify("AUTO_PUSH_FAILED", f"sha={sha}\n{push.stderr[-1200:]}")
        return

    notify("AUTO_PUSH_OK", f"sha={sha}\ntask={task_label}")


def main():
    notify("CYCLE_START", f"repo={REPO}")

    gate_code = enforce_gate_before_dispatch()
    if gate_code:
        return 0

    task = select_task()
    rel_task = task.relative_to(REPO) if task else None
    task_label = str(rel_task) if rel_task else "none"

    set_gate("RUNNING", 0, task_label)
    write_status("RUNNING", f"task={task_label}")

    if task:
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

    set_gate("WAITING_AUDIT", code, task_label)
    write_status("WAITING_AUDIT", f"task={task_label}; cycle closed")
    print("CYCLE_CLOSED_WAITING_AUDIT")

    if code == 0:
        notify("CYCLE_OK", f"cycle closed; gate=WAITING_AUDIT; task={task_label}")
        auto_commit_and_push(rel_task, code)
    else:
        notify("CYCLE_FAIL", f"exit_code={code}; gate=WAITING_AUDIT; task={task_label}")

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
