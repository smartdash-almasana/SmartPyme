# AUTO-INTEGRATED CODEX EXECUTION
# SmartPyme Factory runner: Hermes -> Codex -> Post-cycle control
from pathlib import Path
import subprocess
import sys

REPO = Path(__file__).resolve().parents[1]
CODEX_TASK = REPO / "factory/tasks/template_codex_task.yaml"
CODEX_RUNNER = REPO / "scripts/codex_builder_runner.py"
POST_CYCLE = REPO / "scripts/factory_post_cycle_control.py"


def run_post_cycle(codex_returncode: int) -> int:
    if not POST_CYCLE.exists():
        print("[PostCycle] BLOCKED_POST_CYCLE_SCRIPT_NOT_FOUND")
        return codex_returncode
    result = subprocess.run([
        "python3",
        str(POST_CYCLE),
        "--repo",
        str(REPO),
        "--codex-returncode",
        str(codex_returncode),
    ])
    if result.returncode != 0:
        print(f"[PostCycle] FAILED returncode={result.returncode}")
        return result.returncode
    return codex_returncode


if CODEX_TASK.exists():
    print("[Hermes→Codex] Dispatching task...")
    result = subprocess.run([
        "python3",
        str(CODEX_RUNNER),
        "--repo",
        str(REPO),
        "--full-auto",
        "--timeout",
        "3600",
    ])
    final_code = run_post_cycle(result.returncode)
    sys.exit(final_code)

print("[Hermes] No Codex task, running post-cycle control only.")
final_code = run_post_cycle(0)
sys.exit(final_code)
