from __future__ import annotations

from pydantic_ai import Agent

from factory_prefect.contracts.messages import CodePatchProposal


MODEL_NAME = "openai:gpt-4o-mini"


def get_coder_agent() -> Agent:
    return Agent(
        MODEL_NAME,
        output_type=CodePatchProposal,
        system_prompt=(
            "You are Coder_Agent for SmartPyme Prefect Factory. "
            "Return only a CodePatchProposal. "
            "Do not execute shell commands. "
            "Do not push to git. "
            "Propose minimal, testable code changes only."
        ),
    )
