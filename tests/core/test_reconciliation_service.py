import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.core.reconciliation.service import reconcile_records


def test_happy_path_exact_match():
    source_a = [{"order_id": "o-1", "amount": 100.0, "status": "ok"}]
    source_b = [{"order_id": "o-1", "amount": 100.0, "status": "ok"}]

    result = reconcile_records(source_a, source_b, key_field="order_id")

    assert len(result.matches) == 1
    assert result.matches[0].key == "o-1"
    assert result.mismatches == []
    assert result.missing_in_a == []
    assert result.missing_in_b == []


def test_numeric_mismatch_has_quantified_delta():
    source_a = [{"order_id": "o-2", "amount": 100.0, "status": "ok"}]
    source_b = [{"order_id": "o-2", "amount": 120.5, "status": "ok"}]

    result = reconcile_records(source_a, source_b, key_field="order_id")

    assert result.matches == []
    assert len(result.mismatches) == 1
    mismatch = result.mismatches[0]
    assert mismatch.key == "o-2"
    assert mismatch.field_name == "amount"
    assert mismatch.delta == 20.5
    assert mismatch.detail == "mismatch_numerico"


def test_missing_in_one_source_is_reported():
    source_a = [{"order_id": "o-3", "amount": 30}]
    source_b = [
        {"order_id": "o-3", "amount": 30},
        {"order_id": "o-4", "amount": 40},
    ]

    result = reconcile_records(source_a, source_b, key_field="order_id")

    assert len(result.matches) == 1
    assert result.matches[0].key == "o-3"
    assert len(result.missing_in_a) == 1
    assert result.missing_in_a[0]["order_id"] == "o-4"
    assert result.missing_in_b == []


def test_duplicate_in_source_a_blocks_execution():
    source_a = [
        {"order_id": "dup-1", "amount": 10},
        {"order_id": "dup-1", "amount": 12},
    ]
    source_b = [{"order_id": "dup-1", "amount": 10}]

    with pytest.raises(ValueError, match="KEY_DUPLICADA"):
        reconcile_records(source_a, source_b, key_field="order_id")


def test_null_key_blocks_execution():
    source_a = [{"order_id": None, "amount": 10}]
    source_b = [{"order_id": "x-1", "amount": 10}]

    with pytest.raises(ValueError, match="KEY_FIELD_NULO"):
        reconcile_records(source_a, source_b, key_field="order_id")
