from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

ActionStatus = Literal["proposed", "approved", "rejected", "executed"]


@dataclass(frozen=True, slots=True)
class ActionProposal:
    action_id: str
    source_id: str                      # finding_id or message_id
    source_type: str                    # "finding" | "message"
    title: str
    description: str
    recommended_action: str
    status: ActionStatus = "proposed"
    requires_confirmation: bool = True
    traceable_origin: dict[str, Any] = field(default_factory=dict)
