from __future__ import annotations

import asyncio
import json
from typing import Any

from agent_framework import FunctionExecutor, WorkflowBuilder
from pydantic import BaseModel, Field


class GraphRunRequest(BaseModel):
    workflow_id: str = "ms_af_graph_no_llm_v1"
    hito_id: str = "HITO_MS_AF_02_GRAPH_REAL_NO_LLM"


class GraphStepResult(BaseModel):
    step_id: str
    status: str = "PASS"
    payload: dict[str, Any] = Field(default_factory=dict)


def planner_mock(request: GraphRunRequest) -> GraphStepResult:
    return GraphStepResult(
        step_id="planner_mock",
        payload={
            "workflow_id": request.workflow_id,
            "hito_id": request.hito_id,
            "plan": "graph_plan_created",
        },
    )


def validator_mock(previous: GraphStepResult) -> GraphStepResult:
    return GraphStepResult(
        step_id="validator_mock",
        payload={
            "validated_step": previous.step_id,
            "valid": True,
        },
    )


def publisher_mock(previous: GraphStepResult) -> GraphStepResult:
    return GraphStepResult(
        step_id="publisher_mock",
        payload={
            "published": False,
            "reason": "sandbox_no_git_write",
            "validated_step": previous.step_id,
        },
    )


async def main() -> None:
    planner = FunctionExecutor(
        planner_mock,
        id="planner_mock",
        input=GraphRunRequest,
        output=GraphStepResult,
    )
    validator = FunctionExecutor(
        validator_mock,
        id="validator_mock",
        input=GraphStepResult,
        output=GraphStepResult,
    )
    publisher = FunctionExecutor(
        publisher_mock,
        id="publisher_mock",
        input=GraphStepResult,
        output=GraphStepResult,
        workflow_output=GraphStepResult,
    )

    workflow = (
        WorkflowBuilder(
            name="ms_af_graph_no_llm_v1",
            description="Real Microsoft Agent Framework graph without LLM calls.",
            start_executor=planner,
            output_executors=[publisher],
        )
        .add_edge(planner, validator)
        .add_edge(validator, publisher)
        .build()
    )

    result = await workflow.run(GraphRunRequest())

    print(
        json.dumps(
            {
                "workflow_id": "ms_af_graph_no_llm_v1",
                "status": "PASS",
                "llm_called": False,
                "smartpyme_runtime_touched": False,
                "result_type": type(result).__name__,
                "result": str(result),
            },
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    asyncio.run(main())
