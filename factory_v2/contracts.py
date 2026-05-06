"""Contratos Pydantic mínimos para factory_v2 — POC LangGraph low-cost."""

from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class NodeStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    BLOCKED = "BLOCKED"


class TaskSpecV2(BaseModel):
    """Especificación mínima de tarea para el grafo determinístico."""

    task_id: str = Field(..., description="Identificador único de la tarea")
    objective: str = Field(..., description="Objetivo en una línea")
    files_allowed: List[str] = Field(default_factory=list)
    files_forbidden: List[str] = Field(default_factory=list)
    acceptance_criteria: List[str] = Field(default_factory=list)
    modo: str = Field(default="AUDIT_ONLY", description="AUDIT_ONLY | WRITE_AUTHORIZED")


class ExecutionResultV2(BaseModel):
    """Resultado de la ejecución de un nodo del grafo."""

    task_id: str
    node_name: str
    status: NodeStatus
    stdout: str = ""
    stderr: str = ""
    return_code: int = 0
    evidence_path: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class GraphState(BaseModel):
    """Estado compartido que fluye por el grafo determinístico."""

    task_spec: TaskSpecV2
    audit_result: Optional[ExecutionResultV2] = None
    implement_result: Optional[ExecutionResultV2] = None
    sandbox_result: Optional[ExecutionResultV2] = None
    review_result: Optional[ExecutionResultV2] = None
    generated_code: str = ""
    test_code: str = ""
    halted: bool = False
    halt_reason: str = ""
