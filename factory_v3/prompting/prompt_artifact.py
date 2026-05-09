from __future__ import annotations

from pydantic import BaseModel

from factory_v3.prompting.prompt_contract import PromptContract


class PromptArtifact(BaseModel):
    task_id: str
    agent_id: str
    contract: PromptContract
    rendered_prompt: str

    @classmethod
    def from_contract(
        cls,
        *,
        task_id: str,
        agent_id: str,
        contract: PromptContract,
    ) -> "PromptArtifact":
        return cls(
            task_id=task_id,
            agent_id=agent_id,
            contract=contract,
            rendered_prompt=contract.render(),
        )
