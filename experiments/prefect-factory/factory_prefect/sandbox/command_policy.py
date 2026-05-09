from __future__ import annotations

import re
from dataclasses import dataclass


DANGEROUS_PATTERNS = [
    r"^rm\s",
    r"\brm\s+-rf\b",
    r"^chmod\s",
    r"^chown\s",
    r"^curl\s",
    r"^wget\s",
    r"^gcloud\s",
    r"^terraform\s+apply",
    r"^docker\s+run",
    r"^git\s+push",
]


@dataclass(frozen=True)
class CommandPolicyResult:
    allowed: bool
    requires_human_approval: bool
    reasons: list[str]


def evaluate_command(command: str) -> CommandPolicyResult:
    stripped = command.strip()
    reasons: list[str] = []

    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, stripped):
            reasons.append(f"DANGEROUS_COMMAND_PATTERN:{pattern}")

    if reasons:
        return CommandPolicyResult(
            allowed=False,
            requires_human_approval=True,
            reasons=reasons,
        )

    return CommandPolicyResult(
        allowed=True,
        requires_human_approval=False,
        reasons=[],
    )
