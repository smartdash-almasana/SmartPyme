# AUTO-INTEGRATED CODEX EXECUTION
# (patched minimal integration layer)
from pathlib import Path
import subprocess, sys

REPO = Path(__file__).resolve().parents[1]
CODEX_TASK = REPO / "factory/tasks/template_codex_task.yaml"
CODEX_RUNNER = REPO / "scripts/codex_builder_runner.py"

if CODEX_TASK.exists():
    print("[Hermes→Codex] Dispatching task...")
    result = subprocess.run(["python3", str(CODEX_RUNNER), "--repo", str(REPO)])
    sys.exit(result.returncode)

# fallback to original behavior
from subprocess import run
print("[Hermes] No Codex task, idle.")
