from __future__ import annotations

from enum import Enum

from pydantic import BaseModel


class RefinementCommand(str, Enum):
    SCALE = "V2-ESCALA"
    COST = "V2-COSTO"
    FAILURE = "V2-FALLO"
    ADOPTION = "V2-ADOPCION"
    DEBUG = "V2-DEBUG"
    AFIP = "V2-AFIP"


class RefinementRequest(BaseModel):
    command: RefinementCommand
    target_task_id: str


class RefinementProtocol:
    def next_phase(self, request: RefinementRequest) -> str:
        return request.command.value
