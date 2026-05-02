from __future__ import annotations

import os
import sqlite3
import pytest
from unittest.mock import patch
from app.ai.orchestrators.owner_confirmation_orchestrator import OwnerConfirmationOrchestrator
from app.orchestrator.persistence import _get_db_path

@pytest.fixture
def temp_db(tmp_path, monkeypatch):
    db_file = tmp_path / "jobs.db"
    monkeypatch.setenv("SMARTPYME_JOBS_DB", str(db_file))
    return db_file

@pytest.fixture
def orchestrator():
    return OwnerConfirmationOrchestrator()

def test_confirm_ok_creates_job_in_db(temp_db, orchestrator):
    input_data = {
        "cliente_id": "C1",
        "skill_id": "skill_reconcile_bank_vs_pos",
        "action": "CONFIRM",
        "overrides": {
            "objective": "New Objective",
            "variables": {"pos_total": 100, "bank_total": 100, "periodo": "2026-04"},
            "evidence": ["pos_report", "bank_statement"]
        }
    }
    
    res = orchestrator.confirm_job(input_data)
    
    assert res["status"] == "JOB_CREATED"
    job_id = res["job_id"]
    
    # Verify in DB
    conn = sqlite3.connect(temp_db)
    cursor = conn.execute("SELECT * FROM jobs WHERE job_id = ?", (job_id,))
    row = cursor.fetchone()
    conn.close()
    
    assert row is not None
    # skill_id index depends on schema, but let's check by column name if possible or just existence
    # Based on persistence.py: job_id (0), status (1), current_state (2), skill_id (3), payload_json (4)...
    assert row[1] == "created"
    assert row[3] == "skill_reconcile_bank_vs_pos"

def test_confirm_invalid_input_rejected(orchestrator):
    input_data = {
        "cliente_id": "C1",
        "skill_id": "skill_reconcile_bank_vs_pos",
        "action": "CONFIRM",
        "overrides": {
            "variables": {"pos_total": -50} # Invalid domain
        }
    }
    
    res = orchestrator.confirm_job(input_data)
    assert res["status"] == "REJECTED"
    assert res["error_type"] == "INVALID_INPUT"
    assert "INVALID_RANGE" in res["reason"]

def test_confirm_missing_data_clarification(orchestrator):
    input_data = {
        "cliente_id": "C1",
        "skill_id": "skill_reconcile_bank_vs_pos",
        "action": "CONFIRM",
        "overrides": {
            "variables": {"pos_total": 100} # Missing bank_total, periodo, evidence
        }
    }
    
    res = orchestrator.confirm_job(input_data)
    assert res["status"] == "CLARIFICATION_REQUIRED"
    assert "bank_total" in res["missing_variables"]

def test_confirm_reject_acknowledged(orchestrator):
    input_data = {
        "cliente_id": "C1",
        "skill_id": "skill_x",
        "action": "REJECT",
        "overrides": {}
    }
    
    res = orchestrator.confirm_job(input_data)
    assert res["status"] == "REJECT_ACKNOWLEDGED"

def test_no_extra_fields_in_payload(temp_db, orchestrator):
    input_data = {
        "cliente_id": "C1",
        "skill_id": "skill_reconcile_bank_vs_pos",
        "action": "CONFIRM",
        "overrides": {
            "objective": "Obj",
            "variables": {"pos_total": 100, "bank_total": 100, "periodo": "2026-04", "junk": "extra"},
            "evidence": ["pos_report", "bank_statement"]
        }
    }
    
    res = orchestrator.confirm_job(input_data)
    job_id = res["job_id"]
    
    import json
    conn = sqlite3.connect(temp_db)
    cursor = conn.execute("SELECT payload_json FROM jobs WHERE job_id = ?", (job_id,))
    payload = json.loads(cursor.fetchone()[0])
    conn.close()
    
    assert "junk" not in payload["variables"]
    assert payload["cliente_id"] == "C1"
