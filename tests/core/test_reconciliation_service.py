import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.core.reconciliation.service import (
    analyze_meli_reconciliation,
    analyze_amount_reconciliation,
    apply_human_review_decision,
    build_deterministic_discrepancy_snapshot,
    build_reconciliation_summary,
    calculate_economic_impact,
    claim_reconciliation_jobs,
    complete_reconciliation_job,
    create_reconciliation_job,
    decide_next_action_from_issues,
    detect_deterministic_ambiguity,
    detect_amount_difference,
    evaluate_deterministic_hitl_state,
    evaluate_warnings_fail_closed,
    evaluate_fail_closed_rules,
    fail_reconciliation_job,
    initialize_fail_closed_human_validation,
    raise_if_job_confirmed,
    reconcile_records,
    resolve_deterministic_amount_finding,
    resolve_discrepancy,
    route_amount_reconciliation_for_human_review,
    run_meli_reconciliation,
    run_reconciliation_engine,
)
from app.core.reconciliation.models import HumanReviewDecision, ReconciliationJob, WarningItem


FIXED_NOW = datetime(2026, 4, 22, 12, 0, tzinfo=timezone.utc)


def test_create_reconciliation_job_initializes_pending_job():
    job = create_reconciliation_job(
        job_id="job-1",
        store_id="store-1",
        cursor={"offset": 0},
        now=FIXED_NOW,
    )

    assert job.job_id == "job-1"
    assert job.store_id == "store-1"
    assert job.scope == "orders"
    assert job.cursor == {"offset": 0}
    assert job.status == "pending"
    assert job.attempts == 0
    assert job.next_eligible_at == FIXED_NOW
    assert job.locked_at is None
    assert job.locked_by is None
    assert job.created_at == FIXED_NOW
    assert job.updated_at == FIXED_NOW


def test_create_reconciliation_job_is_fail_closed_for_invalid_scope():
    with pytest.raises(ValueError, match="RECONCILIATION_SCOPE_INVALIDO"):
        create_reconciliation_job(
            job_id="job-2",
            store_id="store-1",
            scope="payments",  # type: ignore[arg-type]
            now=FIXED_NOW,
        )


def test_claim_reconciliation_jobs_claims_eligible_jobs_in_deterministic_order():
    later = FIXED_NOW + timedelta(minutes=1)
    jobs = [
        create_reconciliation_job(job_id="job-b", store_id="store-1", now=FIXED_NOW),
        create_reconciliation_job(job_id="job-a", store_id="store-1", now=FIXED_NOW),
        create_reconciliation_job(job_id="job-later", store_id="store-1", now=later),
    ]

    claimed = claim_reconciliation_jobs(
        jobs,
        worker="worker-a",
        limit=2,
        now=FIXED_NOW,
    )

    assert [job.job_id for job in claimed] == ["job-a", "job-b"]
    assert all(job.status == "running" for job in claimed)
    assert all(job.attempts == 1 for job in claimed)
    assert all(job.locked_at == FIXED_NOW for job in claimed)
    assert all(job.locked_by == "worker-a" for job in claimed)


def test_claim_reconciliation_jobs_skips_locked_and_done_jobs():
    locked = ReconciliationJob(
        job_id="job-locked",
        store_id="store-1",
        status="running",
        attempts=1,
        next_eligible_at=FIXED_NOW,
        locked_at=FIXED_NOW,
        locked_by="worker-a",
        created_at=FIXED_NOW,
        updated_at=FIXED_NOW,
    )
    done = ReconciliationJob(
        job_id="job-done",
        store_id="store-1",
        status="done",
        next_eligible_at=FIXED_NOW,
        created_at=FIXED_NOW,
        updated_at=FIXED_NOW,
    )
    pending = create_reconciliation_job(job_id="job-pending", store_id="store-1", now=FIXED_NOW)

    claimed = claim_reconciliation_jobs(
        [locked, done, pending],
        worker="worker-b",
        now=FIXED_NOW,
    )

    assert [job.job_id for job in claimed] == ["job-pending"]


def test_complete_reconciliation_job_closes_running_job_and_updates_cursor():
    job = claim_reconciliation_jobs(
        [create_reconciliation_job(job_id="job-3", store_id="store-1", now=FIXED_NOW)],
        worker="worker-a",
        now=FIXED_NOW,
    )[0]

    completed = complete_reconciliation_job(
        job,
        cursor={"offset": 50},
        now=FIXED_NOW + timedelta(minutes=5),
    )

    assert completed.status == "done"
    assert completed.cursor == {"offset": 50}
    assert completed.locked_at is None
    assert completed.locked_by is None
    assert completed.last_error is None
    assert completed.updated_at == FIXED_NOW + timedelta(minutes=5)


def test_fail_reconciliation_job_releases_lock_and_schedules_backoff():
    job = claim_reconciliation_jobs(
        [create_reconciliation_job(job_id="job-4", store_id="store-1", now=FIXED_NOW)],
        worker="worker-a",
        now=FIXED_NOW,
    )[0]

    failed = fail_reconciliation_job(
        job,
        error="temporary outage",
        now=FIXED_NOW + timedelta(seconds=10),
    )

    assert failed.status == "failed"
    assert failed.locked_at is None
    assert failed.locked_by is None
    assert failed.last_error == "temporary outage"
    assert failed.next_eligible_at == FIXED_NOW + timedelta(seconds=70)


def test_fail_reconciliation_job_moves_to_dead_letter_at_attempt_threshold():
    job = ReconciliationJob(
        job_id="job-5",
        store_id="store-1",
        status="running",
        attempts=10,
        next_eligible_at=FIXED_NOW,
        locked_at=FIXED_NOW,
        locked_by="worker-a",
        created_at=FIXED_NOW,
        updated_at=FIXED_NOW,
    )

    failed = fail_reconciliation_job(
        job,
        error="reauthorization required",
        now=FIXED_NOW + timedelta(minutes=1),
    )

    assert failed.status == "dead_letter"
    assert failed.dead_letter_at == FIXED_NOW + timedelta(minutes=1)
    assert failed.last_error == "reauthorization required"
    assert failed.locked_at is None
    assert failed.locked_by is None


def test_reconciliation_job_services_are_fail_closed_for_naive_datetime():
    naive_now = datetime(2026, 4, 22, 12, 0)

    with pytest.raises(ValueError, match="NOW_INVALIDO"):
        create_reconciliation_job(
            job_id="job-6",
            store_id="store-1",
            now=naive_now,
        )


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
    assert result.missing_in_a[0].root["order_id"] == "o-4"
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


def test_analyze_amount_reconciliation_returns_findings_for_amount_deltas():
    records = [
        {"order_id": "o-1", "expected_amount": 100.0, "actual_amount": 100.0},
        {"order_id": "o-2", "expected_amount": 80.0, "actual_amount": 75.5},
    ]

    result = analyze_amount_reconciliation(records)

    assert result.total_records == 2
    assert result.ok_records == 1
    assert result.has_blocking_pending is True
    assert len(result.findings) == 1
    finding = result.findings[0]
    assert finding.key == "o-2"
    assert finding.delta == 4.5
    assert finding.blocking is True
    assert finding.reason == "monto_diferente"
    assert finding.clarification_state == "pending_validation"
    assert finding.pending_validation is True
    assert finding.suggested_action == "sugerir_cobro_diferencia"
    assert "Registro o-2" in finding.human_question
    assert result.uncertainty_records == []
    assert result.suggested_actions == [
        "solicitar_revision_humana",
        "sugerir_cobro_diferencia",
    ]
    assert result.human_review_questions == [finding.human_question]
    assert len(result.clarification_questions) == 1
    assert result.clarification_questions[0].key == "o-2"
    assert result.clarification_questions[0].reason == "monto_diferente"
    assert result.clarification_questions[0].clarification_state == "pending_validation"
    assert result.clarification_questions[0].pending_validation is True
    assert result.workflow_decision == "human_review_required"
    assert result.clarification_state == "pending_validation"


def test_analyze_amount_reconciliation_returns_negative_delta_for_overpayment():
    records = [
        {"order_id": "o-2b", "expected_amount": 75.5, "actual_amount": 80.0},
    ]

    result = analyze_amount_reconciliation(records)

    assert result.total_records == 1
    assert result.ok_records == 0
    assert len(result.findings) == 1
    finding = result.findings[0]
    assert finding.delta == -4.5
    assert finding.reason == "monto_diferente"
    assert finding.suggested_action == "sugerir_revision_sobrepago"
    assert "Registro o-2b" in finding.human_question
    assert result.suggested_actions == [
        "solicitar_revision_humana",
        "sugerir_revision_sobrepago",
    ]
    assert result.human_review_questions == [finding.human_question]
    assert result.clarification_state == "pending_validation"


def test_analyze_amount_reconciliation_enforces_deterministic_difference_even_with_tolerance():
    records = [
        {"order_id": "o-3", "expected_amount": 200.0, "actual_amount": 200.04},
    ]

    result = analyze_amount_reconciliation(records, tolerance=0.05)

    assert result.ok_records == 0
    assert len(result.findings) == 1
    assert result.findings[0].reason == "monto_diferente"
    assert result.uncertainty_records == []
    assert result.suggested_actions == [
        "solicitar_revision_humana",
        "sugerir_revision_sobrepago",
    ]
    assert len(result.human_review_questions) == 1
    assert len(result.clarification_questions) == 1
    assert result.workflow_decision == "human_review_required"
    assert result.has_blocking_pending is True
    assert result.clarification_state == "pending_validation"


def test_analyze_amount_reconciliation_marks_uncertainty_as_pending_validation():
    records = [
        {"order_id": "o-5", "expected_amount": 100.0, "actual_amount": 100.03},
    ]

    result = analyze_amount_reconciliation(records, tolerance=0.0, uncertainty_threshold=0.05)

    assert result.total_records == 1
    assert result.ok_records == 0
    assert result.has_blocking_pending is True
    assert result.suggested_actions == ["solicitar_revision_humana"]
    assert len(result.findings) == 1
    finding = result.findings[0]
    assert finding.reason == "monto_incierto"
    assert finding.clarification_state == "pending_validation"
    assert finding.pending_validation is True
    assert finding.suggested_action == "solicitar_revision_humana"
    assert "Registro o-5" in finding.human_question
    assert result.uncertainty_records == []
    assert result.human_review_questions == [finding.human_question]
    assert result.workflow_decision == "human_review_required"
    assert result.clarification_state == "pending_validation"


def test_analyze_amount_reconciliation_fails_closed_for_non_numeric_amount():
    records = [
        {"order_id": "o-4", "expected_amount": "100", "actual_amount": 100.0},
        {"order_id": "o-6", "expected_amount": "abc", "actual_amount": 100.0},
    ]

    result = analyze_amount_reconciliation(records)

    assert result.total_records == 2
    assert result.ok_records == 1
    assert result.has_blocking_pending is True
    assert len(result.findings) == 1
    assert len(result.uncertainty_records) == 1
    finding = result.findings[0]
    uncertainty = result.uncertainty_records[0]
    assert finding.key == "o-6"
    assert finding.reason == "non_numeric"
    assert finding.suggested_action == "solicitar_revision_humana"
    assert "Registro o-6" in finding.human_question
    assert uncertainty.key == "o-6"
    assert uncertainty.field_name == "expected_amount"
    assert uncertainty.reason == "non_numeric"
    assert uncertainty.clarification_state == "pending_validation"
    assert result.suggested_actions == ["solicitar_revision_humana"]
    assert result.human_review_questions == [finding.human_question]
    assert result.workflow_decision == "human_review_required"
    assert result.clarification_state == "pending_validation"


def test_analyze_amount_reconciliation_fails_closed_for_missing_amount_fields():
    records = [
        {"order_id": "o-8", "expected_amount": 150.0},
        {"order_id": "o-9", "actual_amount": 140.0},
    ]

    result = analyze_amount_reconciliation(records)

    assert result.total_records == 2
    assert result.ok_records == 0
    assert result.has_blocking_pending is True
    assert len(result.findings) == 2
    assert all(f.reason == "monto_incierto" for f in result.findings)
    assert all(f.delta == float("inf") for f in result.findings)
    assert len(result.uncertainty_records) == 2
    assert {u.field_name for u in result.uncertainty_records} == {"expected_amount", "actual_amount"}
    assert result.suggested_actions == ["solicitar_revision_humana"]
    assert len(result.human_review_questions) == 2
    assert all("Registro o-" in question for question in result.human_review_questions)
    assert result.workflow_decision == "human_review_required"
    assert result.clarification_state == "pending_validation"


def test_analyze_amount_reconciliation_fails_closed_for_null_amount_fields():
    records = [
        {"order_id": "o-10", "expected_amount": None, "actual_amount": 100.0},
        {"order_id": "o-11", "expected_amount": 100.0, "actual_amount": None},
    ]

    result = analyze_amount_reconciliation(records)

    assert result.total_records == 2
    assert result.ok_records == 0
    assert result.has_blocking_pending is True
    assert len(result.findings) == 2
    assert all(f.reason == "monto_incierto" for f in result.findings)
    assert all(f.delta == float("inf") for f in result.findings)
    assert len(result.uncertainty_records) == 2
    assert {u.field_name for u in result.uncertainty_records} == {"expected_amount", "actual_amount"}
    assert result.suggested_actions == ["solicitar_revision_humana"]
    assert len(result.human_review_questions) == 2
    assert result.workflow_decision == "human_review_required"
    assert result.clarification_state == "pending_validation"


def test_analyze_amount_reconciliation_fails_closed_for_currency_ambiguous_parse():
    records = [
        {"order_id": "o-7", "expected_amount": "1.234,56", "actual_amount": "1234.56"},
    ]

    result = analyze_amount_reconciliation(records)

    assert result.total_records == 1
    assert result.ok_records == 0
    assert result.has_blocking_pending is True
    assert len(result.findings) == 1
    assert len(result.uncertainty_records) == 1
    finding = result.findings[0]
    uncertainty = result.uncertainty_records[0]
    assert finding.key == "o-7"
    assert finding.reason == "currency_ambiguous"
    assert finding.pending_validation is True
    assert "Registro o-7" in finding.human_question
    assert uncertainty.field_name == "expected_amount"
    assert uncertainty.raw_value == "1.234,56"
    assert uncertainty.reason == "currency_ambiguous"
    assert result.human_review_questions == [finding.human_question]
    assert result.clarification_state == "pending_validation"


def test_analyze_amount_reconciliation_supports_source_amount_field_aliases():
    records = [
        {"order_id": "o-15", "amount_expected": 220.0, "amount_paid": 200.0},
    ]

    result = analyze_amount_reconciliation(records)

    assert result.total_records == 1
    assert result.ok_records == 0
    assert result.has_blocking_pending is True
    assert len(result.findings) == 1
    finding = result.findings[0]
    assert finding.key == "o-15"
    assert finding.delta == 20.0
    assert finding.reason == "monto_diferente"
    assert finding.suggested_action == "sugerir_cobro_diferencia"
    assert result.uncertainty_records == []


def test_calculate_economic_impact_classifies_shortfall():
    impact = calculate_economic_impact(expected_amount=120.0, actual_amount=100.0)
    assert impact.delta == 20.0
    assert impact.absolute_delta == 20.0
    assert impact.direction == "shortfall"


def test_calculate_economic_impact_classifies_overpayment():
    impact = calculate_economic_impact(expected_amount=80.0, actual_amount=100.0)
    assert impact.delta == -20.0
    assert impact.absolute_delta == 20.0
    assert impact.direction == "overpayment"


def test_detect_amount_difference_enforces_difference_even_with_tolerance():
    assessment = detect_amount_difference(
        expected_amount=100.0,
        actual_amount=100.03,
        tolerance=0.05,
        uncertainty_threshold=None,
    )
    assert assessment.has_difference is True
    assert assessment.uncertain is False
    assert assessment.reason == "monto_diferente"


def test_detect_amount_difference_marks_uncertainty_with_threshold():
    assessment = detect_amount_difference(
        expected_amount=100.0,
        actual_amount=100.03,
        tolerance=0.0,
        uncertainty_threshold=0.05,
    )
    assert assessment.has_difference is True
    assert assessment.uncertain is True
    assert assessment.reason == "monto_incierto"


def test_resolve_deterministic_amount_finding_returns_none_without_difference():
    finding = resolve_deterministic_amount_finding(
        key="o-18",
        expected_amount=100.0,
        actual_amount=100.0,
        tolerance=0.0,
        uncertainty_threshold=None,
    )

    assert finding is None


def test_route_amount_reconciliation_for_human_review_enforces_fail_closed_with_findings():
    result = analyze_amount_reconciliation(
        [{"order_id": "o-19", "expected_amount": 100.0, "actual_amount": 90.0}]
    )

    state_machine, max_uncertainty_level, suggested_actions = (
        route_amount_reconciliation_for_human_review(
            findings=result.findings,
            uncertainty_levels=[finding.uncertainty_level for finding in result.findings],
            suggested_actions=[],
        )
    )

    assert state_machine.workflow_decision == "human_review_required"
    assert state_machine.clarification_state == "pending_validation"
    assert state_machine.has_blocking_pending is True
    assert max_uncertainty_level == "high"
    assert suggested_actions == ["solicitar_revision_humana"]


def test_decide_next_action_from_issues_routes_human_review_for_high_risk_codes():
    issues = [{"code": "missing_core_fields"}]
    assert decide_next_action_from_issues(issues) == "human_review_required"


def test_decide_next_action_from_issues_routes_guided_for_medium_codes():
    issues = [{"code": "duplicate_rows"}]
    assert decide_next_action_from_issues(issues) == "guided_curation"


def test_decide_next_action_from_issues_is_fail_closed_for_unknown_codes():
    issues = [{"code": "new_unmapped_issue"}]
    assert decide_next_action_from_issues(issues) == "human_review_required"


def test_build_deterministic_discrepancy_snapshot_maps_only_finite_deltas():
    result = analyze_amount_reconciliation(
        [
            {"order_id": "o-19b", "expected_amount": 120.0, "actual_amount": 100.0},
            {"order_id": "o-19c", "expected_amount": "abc", "actual_amount": 100.0},
        ]
    )

    snapshot = build_deterministic_discrepancy_snapshot(result.findings)

    assert len(snapshot.findings) == 2
    assert snapshot.orders_with_diff == 1
    assert snapshot.total_diff_amount == 20.0
    assert snapshot.findings[0]["entity"] == "o-19b"
    assert snapshot.findings[0]["diff"] == 20.0
    assert snapshot.findings[1]["entity"] == "o-19c"
    assert snapshot.findings[1]["diff"] is None


def test_evaluate_deterministic_hitl_state_escalates_fail_closed_on_warnings():
    result = analyze_amount_reconciliation(
        [{"order_id": "o-19d", "expected_amount": 100.0, "actual_amount": 100.0}]
    )

    state = evaluate_deterministic_hitl_state(
        amount_workflow_decision=result.workflow_decision,
        issues=[],
        warnings=[
            WarningItem(
                code="unknown_semantic_mapping",
                message="Manual confirmation required.",
                blocking=True,
            )
        ],
        uncertainty_records=result.uncertainty_records,
        findings=result.findings,
    )

    assert state.amount_decision == "direct_parse"
    assert state.issue_decision == "direct_parse"
    assert state.fail_closed_decision == "human_review_required"
    assert state.workflow_decision == "human_review_required"
    assert state.clarification_state == "pending_validation"
    assert state.has_blocking_pending is True


def test_raise_if_job_confirmed_blocks_mutations():
    with pytest.raises(ValueError, match="JOB_YA_CONFIRMADO"):
        raise_if_job_confirmed({"status": "handoff_confirmed"})


def test_raise_if_job_confirmed_blocks_mutations_with_normalized_status():
    with pytest.raises(ValueError, match="JOB_YA_CONFIRMADO"):
        raise_if_job_confirmed({"status": "  Handoff_Confirmed  "})


def test_raise_if_job_confirmed_blocks_mutations_when_cancelled():
    with pytest.raises(ValueError, match="JOB_YA_CONFIRMADO"):
        raise_if_job_confirmed({"status": "handoff_cancelled"})


def test_raise_if_job_confirmed_is_fail_closed_for_unknown_status():
    with pytest.raises(ValueError, match="RECONCILIATION_STATUS_INVALIDO"):
        raise_if_job_confirmed({"status": "in_progress"})


def test_raise_if_job_confirmed_is_fail_closed_for_non_dict_state():
    with pytest.raises(ValueError, match="RECONCILIATION_STATE_INVALIDO"):
        raise_if_job_confirmed("pending_validation")  # type: ignore[arg-type]


def test_raise_if_job_confirmed_is_fail_closed_for_non_string_status():
    with pytest.raises(ValueError, match="RECONCILIATION_STATUS_INVALIDO"):
        raise_if_job_confirmed({"status": None})


def test_run_reconciliation_engine_blocks_when_job_is_already_confirmed():
    with pytest.raises(ValueError, match="JOB_YA_CONFIRMADO"):
        run_reconciliation_engine(
            [{"order_id": "o-10", "expected_amount": 10.0, "actual_amount": 9.0}],
            job_state={"status": "handoff_confirmed"},
        )


def test_run_reconciliation_engine_is_fail_closed_for_unknown_job_status():
    with pytest.raises(ValueError, match="RECONCILIATION_STATUS_INVALIDO"):
        run_reconciliation_engine(
            [{"order_id": "o-10b", "expected_amount": 10.0, "actual_amount": 9.0}],
            job_state={"status": "in_progress"},
        )


def test_run_reconciliation_engine_is_fail_closed_for_non_dict_job_state():
    with pytest.raises(ValueError, match="RECONCILIATION_STATE_INVALIDO"):
        run_reconciliation_engine(
            [{"order_id": "o-10c", "expected_amount": 10.0, "actual_amount": 9.0}],
            job_state="pending_validation",  # type: ignore[arg-type]
        )


def test_run_reconciliation_engine_escalates_to_human_review_for_risky_issues():
    result = run_reconciliation_engine(
        [{"order_id": "o-11", "expected_amount": 100.0, "actual_amount": 100.0}],
        issues=[{"code": "missing_core_fields"}],
    )

    assert result.workflow_decision == "human_review_required"
    assert result.has_blocking_pending is True
    assert result.suggested_actions == ["solicitar_revision_humana"]
    assert result.clarification_state == "pending_validation"


def test_run_reconciliation_engine_keeps_direct_parse_when_no_diffs_or_issues():
    result = run_reconciliation_engine(
        [{"order_id": "o-12", "expected_amount": 100.0, "actual_amount": 100.0}],
    )

    assert result.workflow_decision == "direct_parse"
    assert result.has_blocking_pending is False
    assert result.suggested_actions == []
    assert result.clarification_state == "no_requiere"


def test_evaluate_warnings_fail_closed_blocks_on_critical_semantic_warning():
    warnings = [
        WarningItem(
            code="color_semantics_out_of_scope",
            message="Color semantics are ambiguous for this source.",
        )
    ]

    decision = evaluate_warnings_fail_closed(warnings)

    assert decision == "human_review_required"


def test_detect_deterministic_ambiguity_flags_currency_ambiguous():
    parsed_value, reason = detect_deterministic_ambiguity("1.234,56")

    assert parsed_value is None
    assert reason == "currency_ambiguous"


def test_detect_deterministic_ambiguity_flags_non_numeric_value():
    parsed_value, reason = detect_deterministic_ambiguity("abc")

    assert parsed_value is None
    assert reason == "non_numeric"


def test_evaluate_fail_closed_rules_returns_combined_trigger():
    state = evaluate_fail_closed_rules(
        warnings=[
            WarningItem(
                code="unknown_semantic_mapping",
                message="Requiere confirmacion humana.",
                blocking=True,
            )
        ],
        uncertainty_records=[],
        findings=[
            analyze_amount_reconciliation(
                [{"order_id": "o-17", "expected_amount": 100.0, "actual_amount": 98.0}]
            ).findings[0]
        ],
    )

    assert state.workflow_decision == "human_review_required"
    assert state.clarification_state == "pending_validation"
    assert state.has_blocking_pending is True
    assert state.trigger == "warnings_and_uncertainties"


def test_run_reconciliation_engine_escalates_when_blocking_warning_exists():
    result = run_reconciliation_engine(
        [{"order_id": "o-13", "expected_amount": 100.0, "actual_amount": 100.0}],
        warnings=[
            WarningItem(
                code="unknown_semantic_mapping",
                message="Semantic mapping requires manual confirmation.",
                blocking=True,
            )
        ],
    )

    assert result.workflow_decision == "human_review_required"
    assert result.has_blocking_pending is True
    assert result.suggested_actions == ["solicitar_revision_humana"]
    assert result.clarification_state == "pending_validation"
    assert len(result.warnings) == 1
    assert result.warnings[0].code == "unknown_semantic_mapping"


def test_run_reconciliation_engine_accumulates_and_deduplicates_warnings():
    warning = WarningItem(
        code="unknown_semantic_mapping",
        message="Requires manual confirmation.",
        key="o-13b",
    )
    result = run_reconciliation_engine(
        [{"order_id": "o-13b", "expected_amount": 100.0, "actual_amount": 100.0}],
        warnings=[warning, warning],
    )

    assert len(result.warnings) == 1
    assert result.warnings[0] == warning


def test_run_reconciliation_engine_keeps_warning_variants_with_different_details():
    result = run_reconciliation_engine(
        [{"order_id": "o-13c", "expected_amount": 100.0, "actual_amount": 100.0}],
        warnings=[
            WarningItem(
                code="color_semantics_out_of_scope",
                message="Color semantics unresolved.",
                details={"palette": "legacy"},
            ),
            WarningItem(
                code="color_semantics_out_of_scope",
                message="Color semantics unresolved.",
                details={"palette": "partner-x"},
            ),
        ],
    )

    assert result.workflow_decision == "human_review_required"
    assert result.clarification_state == "pending_validation"
    assert len(result.warnings) == 2
    assert result.warnings[0].details == {"palette": "legacy"}
    assert result.warnings[1].details == {"palette": "partner-x"}


def test_build_reconciliation_summary_blocks_when_warning_is_fail_closed():
    result = analyze_amount_reconciliation(
        [{"order_id": "o-14", "expected_amount": 100.0, "actual_amount": 100.0}]
    )
    summary = build_reconciliation_summary(
        result,
        warnings=[
            WarningItem(
                code="color_semantics_out_of_scope",
                message="Color semantics unresolved for source columns.",
            )
        ],
    )

    assert summary["status"] == "blocked"
    assert summary["human_in_the_loop"] is True
    assert summary["workflow_decision"] == "human_review_required"
    assert summary["fail_closed_trigger"] == "warnings"


def test_build_reconciliation_summary_uses_accumulated_result_warnings_by_default():
    result = run_reconciliation_engine(
        [{"order_id": "o-14c", "expected_amount": 100.0, "actual_amount": 100.0}],
        warnings=[
            WarningItem(
                code="color_semantics_out_of_scope",
                message="Color semantics unresolved.",
            ),
            WarningItem(
                code="color_semantics_out_of_scope",
                message="Color semantics unresolved.",
            ),
        ],
    )
    summary = build_reconciliation_summary(result)

    assert summary["status"] == "blocked"
    assert summary["fail_closed_trigger"] == "warnings"
    assert len(summary["warnings"]) == 1


def test_initialize_fail_closed_human_validation_blocks_on_uncertainty_only():
    result = analyze_amount_reconciliation(
        [{"order_id": "o-14b", "expected_amount": "abc", "actual_amount": 100.0}]
    )

    state = initialize_fail_closed_human_validation(
        warnings=None,
        uncertainty_records=result.uncertainty_records,
        findings=result.findings,
    )

    assert state.workflow_decision == "human_review_required"
    assert state.clarification_state == "pending_validation"
    assert state.has_blocking_pending is True
    assert state.trigger == "uncertainties"


def test_apply_human_review_decision_confirms_pending_job():
    state = {"status": "pending_validation", "job_id": "r-1"}
    decision = HumanReviewDecision(verdict="confirm", actor="auditor_a", note="validado")

    resolved = apply_human_review_decision(state, decision)

    assert resolved["status"] == "handoff_confirmed"
    assert resolved["human_review_actor"] == "auditor_a"
    assert resolved["human_review_verdict"] == "confirm"
    assert resolved["human_review_note"] == "validado"


def test_apply_human_review_decision_cancels_pending_job():
    state = {"status": "pending_validation", "job_id": "r-2"}
    decision = HumanReviewDecision(verdict="cancel", actor="auditor_b")

    resolved = apply_human_review_decision(state, decision)

    assert resolved["status"] == "handoff_cancelled"
    assert resolved["human_review_actor"] == "auditor_b"
    assert resolved["human_review_verdict"] == "cancel"


def test_apply_human_review_decision_supports_injected_persistence():
    state = {"status": "pending_validation", "job_id": "r-2b"}
    decision = HumanReviewDecision(verdict="confirm", actor="auditor_persist")

    def persist(
        previous_state: dict[str, str],
        incoming_decision: HumanReviewDecision,
        next_state: dict[str, str],
    ) -> dict[str, str]:
        assert previous_state["job_id"] == "r-2b"
        assert incoming_decision.verdict == "confirm"
        persisted = dict(next_state)
        persisted["persisted"] = "yes"
        return persisted

    resolved = apply_human_review_decision(state, decision, persist_decision=persist)

    assert resolved["status"] == "handoff_confirmed"
    assert resolved["human_review_actor"] == "auditor_persist"
    assert resolved["persisted"] == "yes"


def test_apply_human_review_decision_is_fail_closed_when_persistence_fails():
    state = {"status": "pending_validation", "job_id": "r-2c"}
    decision = HumanReviewDecision(verdict="confirm", actor="auditor_persist")

    def persist_raises(
        previous_state: dict[str, str],
        incoming_decision: HumanReviewDecision,
        next_state: dict[str, str],
    ) -> dict[str, str]:
        _ = (previous_state, incoming_decision, next_state)
        raise RuntimeError("db down")

    with pytest.raises(ValueError, match="HUMAN_REVIEW_PERSISTENCE_FALLIDA"):
        apply_human_review_decision(state, decision, persist_decision=persist_raises)


def test_apply_human_review_decision_is_fail_closed_for_invalid_verdict():
    state = {"status": "pending_validation", "job_id": "r-2d"}
    decision = HumanReviewDecision(verdict="other", actor="auditor_x")  # type: ignore[arg-type]

    with pytest.raises(ValueError, match="VERDICT_INVALIDO"):
        apply_human_review_decision(state, decision)


def test_apply_human_review_decision_is_fail_closed_when_persistence_reopens_status():
    state = {"status": "pending_validation", "job_id": "r-2e"}
    decision = HumanReviewDecision(verdict="confirm", actor="auditor_guard")

    def persist_reopens(
        previous_state: dict[str, str],
        incoming_decision: HumanReviewDecision,
        next_state: dict[str, str],
    ) -> dict[str, str]:
        _ = (previous_state, incoming_decision)
        reopened = dict(next_state)
        reopened["status"] = "pending_validation"
        return reopened

    with pytest.raises(ValueError, match="HUMAN_REVIEW_PERSISTENCE_MUTATION_DENEGADA"):
        apply_human_review_decision(state, decision, persist_decision=persist_reopens)


def test_apply_human_review_decision_is_fail_closed_when_persistence_mutates_actor():
    state = {"status": "pending_validation", "job_id": "r-2f"}
    decision = HumanReviewDecision(verdict="confirm", actor="auditor_guard")

    def persist_mutates_actor(
        previous_state: dict[str, str],
        incoming_decision: HumanReviewDecision,
        next_state: dict[str, str],
    ) -> dict[str, str]:
        _ = (previous_state, incoming_decision)
        mutated = dict(next_state)
        mutated["human_review_actor"] = "otro_actor"
        return mutated

    with pytest.raises(ValueError, match="HUMAN_REVIEW_PERSISTENCE_MUTATION_DENEGADA"):
        apply_human_review_decision(state, decision, persist_decision=persist_mutates_actor)


def test_apply_human_review_decision_is_fail_closed_when_persistence_mutates_verdict():
    state = {"status": "pending_validation", "job_id": "r-2g"}
    decision = HumanReviewDecision(verdict="confirm", actor="auditor_guard")

    def persist_mutates_verdict(
        previous_state: dict[str, str],
        incoming_decision: HumanReviewDecision,
        next_state: dict[str, str],
    ) -> dict[str, str]:
        _ = (previous_state, incoming_decision)
        mutated = dict(next_state)
        mutated["human_review_verdict"] = "cancel"
        return mutated

    with pytest.raises(ValueError, match="HUMAN_REVIEW_PERSISTENCE_MUTATION_DENEGADA"):
        apply_human_review_decision(state, decision, persist_decision=persist_mutates_verdict)


def test_apply_human_review_decision_is_fail_closed_when_persistence_mutates_note():
    state = {"status": "pending_validation", "job_id": "r-2h"}
    decision = HumanReviewDecision(verdict="confirm", actor="auditor_guard", note="nota_original")

    def persist_mutates_note(
        previous_state: dict[str, str],
        incoming_decision: HumanReviewDecision,
        next_state: dict[str, str],
    ) -> dict[str, str]:
        _ = (previous_state, incoming_decision)
        mutated = dict(next_state)
        mutated["human_review_note"] = "nota_mutada"
        return mutated

    with pytest.raises(ValueError, match="HUMAN_REVIEW_PERSISTENCE_MUTATION_DENEGADA"):
        apply_human_review_decision(state, decision, persist_decision=persist_mutates_note)


def test_apply_human_review_decision_is_fail_closed_for_unknown_state():
    state = {"status": "direct_parse"}
    decision = HumanReviewDecision(verdict="confirm", actor="auditor_a")

    with pytest.raises(ValueError, match="RECONCILIATION_STATUS_INVALIDO"):
        apply_human_review_decision(state, decision)


def test_resolve_discrepancy_confirms_pending_job():
    state = {"status": "pending_validation", "job_id": "r-3"}
    decision = HumanReviewDecision(verdict="confirm", actor="auditor_c")

    resolved = resolve_discrepancy(state, decision)

    assert resolved["status"] == "handoff_confirmed"
    assert resolved["human_review_actor"] == "auditor_c"
    assert resolved["human_review_verdict"] == "confirm"


def test_resolve_discrepancy_blocks_when_job_already_confirmed():
    state = {"status": "handoff_confirmed", "job_id": "r-4"}
    decision = HumanReviewDecision(verdict="cancel", actor="auditor_d")

    with pytest.raises(ValueError, match="JOB_YA_CONFIRMADO"):
        resolve_discrepancy(state, decision)


def test_analyze_meli_reconciliation_detects_deterministic_differences():
    result = analyze_meli_reconciliation(
        [
            {"order_id": "m-1", "amount_expected": 100.0, "amount_paid": 90.0},
            {"order_id": "m-2", "expected_amount": 50.0, "actual_amount": 50.0},
        ]
    )

    assert result["summary"]["total_orders"] == 2
    assert result["summary"]["orders_with_diff"] == 1
    assert result["summary"]["total_diff_amount"] == 10.0
    assert result["summary"]["estimated_recoverable_amount"] == 10.0
    assert len(result["findings"]) == 1
    assert result["findings"][0]["entity"] == "m-1"
    assert result["findings"][0]["diff"] == 10.0
    assert result["findings"][0]["pending_validation"] is True
    assert result["summary"]["clarification_state"] == "pending_validation"
    assert result["summary"]["workflow_decision"] == "human_review_required"
    assert [action["action_type"] for action in result["suggested_actions"]] == [
        "solicitar_revision_humana",
        "generar_documento",
    ]
    document_action = result["suggested_actions"][1]
    assert document_action["economic_impact"] == 10.0
    assert document_action["payload"]["template"] == "meli_reconciliation_diff"
    assert document_action["payload"]["data"]["orders_with_diff"] == 1
    assert document_action["payload"]["data"]["requires_human_validation"] is True


def test_analyze_meli_reconciliation_fail_closed_for_uncertain_amounts():
    result = analyze_meli_reconciliation(
        [
            {"order_id": "m-3", "amount_expected": "abc", "amount_paid": "50"},
        ]
    )

    assert result["summary"]["total_orders"] == 1
    assert result["summary"]["orders_with_diff"] == 0
    assert result["summary"]["total_diff_amount"] == 0.0
    assert result["summary"]["workflow_decision"] == "human_review_required"
    assert result["summary"]["clarification_state"] == "pending_validation"
    assert result["summary"]["has_blocking_pending"] is True
    assert len(result["summary"]["human_review_questions"]) == 1
    assert result["findings"][0]["diff"] is None
    assert result["findings"][0]["money_impact"] is None
    assert result["findings"][0]["reason"] == "non_numeric"
    assert result["suggested_actions"][0]["action_type"] == "solicitar_revision_humana"


def test_analyze_meli_reconciliation_is_fail_closed_for_non_list_rows():
    with pytest.raises(ValueError, match="ROW_INVALIDA"):
        analyze_meli_reconciliation({"order_id": "m-3b"})  # type: ignore[arg-type]


def test_analyze_meli_reconciliation_is_fail_closed_for_non_dict_row_item():
    with pytest.raises(ValueError, match="ROW_INVALIDA"):
        analyze_meli_reconciliation(
            [
                {"order_id": "m-3c", "amount_expected": 100.0, "amount_paid": 100.0},
                "invalid_row",
            ]
        )


def test_run_meli_reconciliation_blocks_confirmed_job_fail_closed():
    with pytest.raises(ValueError, match="JOB_YA_CONFIRMADO"):
        run_meli_reconciliation(
            [{"order_id": "m-4", "amount_expected": 100.0, "amount_paid": 95.0}],
            job_state={"status": "handoff_confirmed"},
        )

