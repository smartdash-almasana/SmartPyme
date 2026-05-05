from __future__ import annotations

from pydantic_ai import Agent

from factory_prefect.contracts.messages import CodePatchProposal


Coder_Agent = Agent(
    "openai:gpt-4o-mini",
    output_type=CodePatchProposal,
    system_prompt=(
        "You are Coder_Agent for SmartPyme Prefect Factory. "
        "Return only a CodePatchProposal. "
        "Do not execute shell commands. "
        "Do not push to git. "
        "Propose minimal, testable code changes only."
    ),
)
