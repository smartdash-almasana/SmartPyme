from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ArtifactReport(BaseModel):
    """
    Contrato soberano para los resultados de una ejecución de tarea en la factoría.
    Este objeto es el principal producto de un worker y alimenta el ArtifactLedger.
    """

    task_id: str
    final_status: str = Field(..., description="Estado final: PASS, FAILED, NEEDS_CORRECTION, BLOCKED")
    target_branch: str
    end_commit_hash: str | None = None

    tests_passed: int = 0
    tests_failed: int = 0
    failed_tests: list[str] = Field(default_factory=list)

    artifact_paths: dict[str, str] = Field(
        default_factory=dict,
        description="Mapeo de tipo de artefacto a su ruta, e.g., {'log': 'path/to/run.log'}"
    )

    execution_time_seconds: float = 0.0
    worker_model: str | None = None
    risk_level: str = "UNKNOWN"
    verdict_message: str
