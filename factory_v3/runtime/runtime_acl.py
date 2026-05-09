from __future__ import annotations

from enum import Enum
from typing import Dict, Set


class RuntimePermission(str, Enum):
    EXECUTE_TASK = "execute_task"
    READ_ARTIFACT = "read_artifact"
    WRITE_ARTIFACT = "write_artifact"
    REQUEST_APPROVAL = "request_approval"
    DISPATCH_TASK = "dispatch_task"


class RuntimeACL:
    def __init__(self):
        self._permissions: Dict[str, Set[RuntimePermission]] = {}

    def grant(self, agent_id: str, permission: RuntimePermission) -> None:
        self._permissions.setdefault(agent_id, set()).add(permission)

    def revoke(self, agent_id: str, permission: RuntimePermission) -> None:
        if agent_id in self._permissions:
            self._permissions[agent_id].discard(permission)

    def allowed(self, agent_id: str, permission: RuntimePermission) -> bool:
        return permission in self._permissions.get(agent_id, set())
