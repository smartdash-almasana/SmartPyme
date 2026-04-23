import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.core.validation.service import validate_data

def test_validate_data_valid():
    result = validate_data({"key": "value"})
    assert result.is_valid is True

def test_validate_data_invalid():
    result = validate_data({})
    assert result.is_valid is False
    assert result.reason == "Data is empty"
