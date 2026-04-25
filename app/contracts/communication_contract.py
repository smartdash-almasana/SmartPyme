from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class FindingMessage:
    message_id: str
    finding_id: str
    channel: str                        # e.g. "internal", "telegram", "whatsapp"
    title: str                          # one-line summary: what happened
    body: str                           # full human-readable explanation
    action_text: str                    # what to do next
    severity: str                       # mirrors Finding.severity
    traceable_origin: dict[str, Any] = field(default_factory=dict)


def build_message_id(finding_id: str, channel: str) -> str:
    digest = hashlib.sha256(f"{finding_id}:{channel}".encode()).hexdigest()
    return f"msg_{digest[:16]}"
