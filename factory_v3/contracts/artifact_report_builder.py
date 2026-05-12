from __future__ import annotations

from collections.abc import Mapping, Sequence

from factory_v3.contracts.artifacts import ArtifactReport


class ArtifactReportBuilder:
    """Build ArtifactReport instances from execution result fields."""

    def build(
        self,
        *,
        task_id: str,
        final_status: str,
        target_branch: str,
        verdict_message: str,
        end_commit_hash: str | None = None,
        tests_passed: int = 0,
        tests_failed: int = 0,
        failed_tests: Sequence[str] | None = None,
        artifact_paths: Mapping[str, str] | None = None,
        execution_time_seconds: float = 0.0,
        worker_model: str | None = None,
        risk_level: str = "UNKNOWN",
    ) -> ArtifactReport:
        return ArtifactReport(
            task_id=task_id,
            final_status=final_status,
            target_branch=target_branch,
            end_commit_hash=end_commit_hash,
            tests_passed=tests_passed,
            tests_failed=tests_failed,
            failed_tests=list(failed_tests or []),
            artifact_paths=dict(artifact_paths or {}),
            execution_time_seconds=execution_time_seconds,
            worker_model=worker_model,
            risk_level=risk_level,
            verdict_message=verdict_message,
        )
