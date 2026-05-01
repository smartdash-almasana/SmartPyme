import os
import sys
from pathlib import Path

import pytest


def test_hermes_run_agent_import_from_vm_repo_path():
    hermes_repo_path = Path(os.environ.get("HERMES_REPO_PATH", "/data/repos/hermes-agent"))
    if not hermes_repo_path.exists():
        pytest.skip(
            "Hermes repo path not available. Set HERMES_REPO_PATH=..."
        )

    hermes_path = str(hermes_repo_path)
    if sys.path[:1] != [hermes_path] and hermes_path in sys.path:
        sys.path.remove(hermes_path)
    if sys.path[:1] != [hermes_path]:
        sys.path.insert(0, hermes_path)

    from run_agent import AIAgent

    assert AIAgent is not None
