import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.core.orchestrator.service import orchestrate

def test_orchestrate():
    result = orchestrate()
    assert result.success is True
