from factory.control.dry_run_cycle import run_dry_run_cycle


def test_factory_dry_run_cycle(tmp_path):
    result = run_dry_run_cycle(task_id="TASK-2026-04-28-999", evidence_root=tmp_path)
    assert result["build_status"] == "BUILD_SUCCESS"
    assert result["audit_status"] == "AUDIT_PASSED"
    assert result["final_state"] == "AWAITING_HUMAN_MERGE"
    assert result["callback_data_bytes"] <= 64
