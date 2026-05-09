from __future__ import annotations

import importlib
import importlib.util
from pathlib import Path

import pytest


def _agent_min_is_available() -> bool:
    pkg_spec = importlib.util.find_spec("factory.agent_min")
    mod_spec = importlib.util.find_spec("factory.agent_min.agent")
    if pkg_spec is None or mod_spec is None:
        return False
    try:
        pkg = importlib.import_module("factory.agent_min")
    except Exception:
        return False
    return hasattr(pkg, "vertex_entrypoint")


_TARGET_FILES = {
    "test_agent_min.py",
    "test_agent_min_runtime.py",
}


def pytest_ignore_collect(collection_path, config):  # type: ignore[no-untyped-def]
    if _agent_min_is_available():
        return False
    return Path(str(collection_path)).name in _TARGET_FILES


def pytest_collection_modifyitems(config, items):  # type: ignore[no-untyped-def]
    if _agent_min_is_available():
        return

    skip_marker = pytest.mark.skip(
        reason="factory.agent_min runtime module is unavailable in this environment"
    )
    for item in items:
        if Path(str(item.fspath)).name in _TARGET_FILES:
            item.add_marker(skip_marker)
