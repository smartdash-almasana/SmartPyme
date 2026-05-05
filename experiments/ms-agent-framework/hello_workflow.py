#!/usr/bin/env python3
"""Deterministic sandbox workflow for Microsoft Agent Framework evaluation.

This script intentionally does not call any LLM provider. It validates the
shape of an explicit workflow spec and executes mock steps in declared order.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any


SPEC_PATH = Path(__file__).with_name("workflow_spec.json")


@dataclass(frozen=True)
class SandboxRunRequest:
    workflow_id: str
    hito_id: str = "HITO_MS_AF_SANDBOX_HELLO"


@dataclass(frozen=True)
class SandboxStepResult:
    step_id: str
    status: str
    payload: dict[str, Any]


def load_spec(path: Path = SPEC_PATH) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def planner_mock(request: SandboxRunRequest) -> SandboxStepResult:
    return SandboxStepResult(
        step_id="planner_mock",
        status="PASS",
        payload={"workflow_id": request.workflow_id, "hito_id": request.hito_id},
    )


def validator_mock(previous: SandboxStepResult) -> SandboxStepResult:
    return SandboxStepResult(
        step_id="validator_mock",
        status="PASS",
        payload={"validated_step": previous.step_id, "valid": previous.status == "PASS"},
    )


def publisher_mock(previous: SandboxStepResult) -> SandboxStepResult:
    return SandboxStepResult(
        step_id="publisher_mock",
        status="PASS",
        payload={"published": False, "reason": "sandbox_no_git_write", "validated_step": previous.step_id},
    )


STEP_FUNCTIONS = {
    "planner_mock": planner_mock,
    "validator_mock": validator_mock,
    "publisher_mock": publisher_mock,
}


def run_workflow() -> dict[str, Any]:
    spec = load_spec()
    request = SandboxRunRequest(workflow_id=spec["workflow_id"])
    current: SandboxRunRequest | SandboxStepResult = request
    executed_steps: list[str] = []
    results: list[dict[str, Any]] = []

    for step in spec["steps"]:
        step_id = step["step_id"]
        step_fn = STEP_FUNCTIONS[step_id]
        current = step_fn(current)  # type: ignore[arg-type]
        executed_steps.append(step_id)
        results.append(asdict(current))

    expected_steps = [step["step_id"] for step in spec["steps"]]
    status = "PASS" if executed_steps == expected_steps and all(result["status"] == "PASS" for result in results) else "FAIL"

    return {
        "workflow_id": spec["workflow_id"],
        "status": status,
        "steps": executed_steps,
        "llm_called": False,
        "smartpyme_runtime_touched": False,
        "results": results,
    }


if __name__ == "__main__":
    print(json.dumps(run_workflow(), ensure_ascii=False, indent=2))
