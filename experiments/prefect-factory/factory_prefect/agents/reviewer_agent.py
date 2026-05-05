from __future__ import annotations

from pydantic_ai import Agent

from factory_prefect.contracts.messages import ReviewDecision


MODEL_NAME = "openai:gpt-4o-mini"


def get_reviewer_agent() -> Agent:
    return Agent(
        MODEL_NAME,
        output_type=ReviewDecision,
        system_prompt=(
            "You are Reviewer_Agent for SmartPyme Prefect Factory. "
            "Validate proposals against Pydantic contracts, allowed paths, "
            "forbidden paths and sandbox command policy. "
            "If risk requires human approval, return HUMAN_REQUIRED."
        ),
    )
