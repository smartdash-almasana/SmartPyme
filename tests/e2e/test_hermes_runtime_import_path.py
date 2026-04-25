import os
from pathlib import Path
import sys

import pytest

smartpyme_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(smartpyme_root))

from app.runtime.hermes_smartpyme_runtime import HermesSmartPymeRuntime


def test_runtime_loads_ai_agent_from_explicit_hermes_repo_path():
    hermes_repo_path = Path(os.environ.get("HERMES_REPO_PATH", "/data/repos/hermes-agent"))
    if not hermes_repo_path.exists():
        pytest.skip(
            "Hermes repo path not available. Set HERMES_REPO_PATH=..."
        )

    runtime = HermesSmartPymeRuntime(hermes_repo_path=hermes_repo_path)
    ai_agent_class = runtime.load_ai_agent_class()

    assert ai_agent_class is not None


def test_runtime_from_env_uses_configurable_hermes_repo_path(monkeypatch):
    hermes_repo_path = Path(os.environ.get("HERMES_REPO_PATH", "/data/repos/hermes-agent"))
    if not hermes_repo_path.exists():
        pytest.skip(
            "Hermes repo path not available. Set HERMES_REPO_PATH=..."
        )

    monkeypatch.setenv("HERMES_REPO_PATH", str(hermes_repo_path))
    runtime = HermesSmartPymeRuntime.from_env()
    ai_agent_class = runtime.load_ai_agent_class()

    assert ai_agent_class is not None
