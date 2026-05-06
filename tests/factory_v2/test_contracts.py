"""Tests de contratos Pydantic para factory_v2."""

import pytest
from pydantic import ValidationError

from factory_v2.contracts import ExecutionResultV2, NodeStatus, TaskSpecV2


class TestTaskSpecV2:
    def test_valido_minimo(self):
        spec = TaskSpecV2(task_id="T-001", objective="Crear función saludar")
        assert spec.task_id == "T-001"
        assert spec.objective == "Crear función saludar"
        assert spec.files_allowed == []
        assert spec.files_forbidden == []
        assert spec.acceptance_criteria == []
        assert spec.modo == "AUDIT_ONLY"

    def test_valido_completo(self):
        spec = TaskSpecV2(
            task_id="T-002",
            objective="Implementar endpoint GET /health",
            files_allowed=["app/api/health.py"],
            files_forbidden=["app/core/"],
            acceptance_criteria=["status 200", "response JSON"],
            modo="WRITE_AUTHORIZED",
        )
        assert spec.modo == "WRITE_AUTHORIZED"
        assert len(spec.files_allowed) == 1

    def test_invalido_sin_task_id(self):
        with pytest.raises(ValidationError):
            TaskSpecV2(objective="Hacer algo")  # type: ignore[arg-type]

    def test_invalido_sin_objective(self):
        with pytest.raises(ValidationError):
            TaskSpecV2(task_id="T-003")  # type: ignore[arg-type]


class TestExecutionResultV2:
    def test_valido_pass(self):
        result = ExecutionResultV2(
            task_id="T-001",
            node_name="audit",
            status=NodeStatus.PASS,
        )
        assert result.status == NodeStatus.PASS
        assert result.return_code == 0
        assert result.timestamp is not None

    def test_valido_fail(self):
        result = ExecutionResultV2(
            task_id="T-001",
            node_name="sandbox",
            status=NodeStatus.FAIL,
            stderr="Error de sintaxis",
            return_code=1,
        )
        assert result.status == NodeStatus.FAIL
        assert "Error de sintaxis" in result.stderr

    def test_valido_blocked(self):
        result = ExecutionResultV2(
            task_id="T-001",
            node_name="audit",
            status=NodeStatus.BLOCKED,
            stderr="Scope no permitido",
            return_code=1,
        )
        assert result.status == NodeStatus.BLOCKED
