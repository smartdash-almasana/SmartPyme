import pytest
from pydantic import ValidationError

from factory_v3.contracts.artifacts import ArtifactReport


def test_artifact_report_serializacion_basica():
    """Verifica que un reporte básico se puede crear y serializar."""
    report = ArtifactReport(
        task_id="t-123",
        final_status="PASS",
        target_branch="main",
        end_commit_hash="a1b2c3d",
        tests_passed=10,
        verdict_message="All good",
    )
    assert report.task_id == "t-123"
    assert report.risk_level == "UNKNOWN"  # Default
    assert report.failed_tests == []  # Default

    # Test JSON serialization/deserialization
    report_json = report.model_dump_json()
    report_deserialized = ArtifactReport.model_validate_json(report_json)
    assert report == report_deserialized


def test_artifact_report_con_fallos():
    """Verifica que un reporte con fallos de test se maneja correctamente."""
    failed_list = ["test_uno", "test_dos"]
    report = ArtifactReport(
        task_id="t-456",
        final_status="NEEDS_CORRECTION",
        target_branch="fix/this",
        end_commit_hash="e4f5g6h",
        tests_passed=8,
        tests_failed=2,
        failed_tests=failed_list,
        risk_level="HIGH",
        verdict_message="Some tests failed",
    )
    assert report.tests_failed == 2
    assert report.failed_tests == failed_list
    assert report.risk_level == "HIGH"


def test_artifact_report_campos_obligatorios():
    """Verifica que los campos obligatorios son validados."""
    with pytest.raises(ValidationError) as excinfo:
        ArtifactReport(task_id="t-789", target_branch="some-branch", verdict_message="msg")

    errors = excinfo.value.errors()
    error_fields = {e["loc"][0] for e in errors}
    # Solo final_status debe faltar ahora
    assert "final_status" in error_fields
    assert len(error_fields) == 1
