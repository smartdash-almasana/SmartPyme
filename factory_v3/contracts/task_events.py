from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, Field

from factory_v3.contracts.entities import TaskState


class TaskEventType(str, Enum):
    CREATED = "created"
    ASSIGNED = "assigned"
    STATE_CHANGED = "state_changed"
    ARTIFACT_LINKED = "artifact_linked"
    BLOCKED = "blocked"
    FAILED = "failed"
    COMPLETED = "completed"


class TaskEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid4()))
    task_id: str
    event_type: TaskEventType
    created_at: datetime = Field(default_factory=datetime.utcnow)
    producer_id: str
    previous_state: Optional[TaskState] = None
    next_state: Optional[TaskState] = None
    linked_artifact_id: Optional[str] = None
    reason: Optional[str] = None
    metadata: dict = Field(default_factory=dict)
