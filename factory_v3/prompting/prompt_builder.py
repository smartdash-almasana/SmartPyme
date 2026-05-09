from __future__ import annotations

from factory_v3.prompting.context_composer import ContextComposer
from factory_v3.prompting.prompt_artifact import PromptArtifact
from factory_v3.prompting.prompt_contract import PromptContract
from factory_v3.prompting.prompt_doctor import PromptDoctor


class PromptBuilder:
    def __init__(self):
        self.context_composer = ContextComposer()
        self.prompt_doctor = PromptDoctor()

    def build(
        self,
        *,
        task_id: str,
        agent_id: str,
        role: str,
        instruction: str,
        artifacts: list[str],
        constraints: list[str],
        examples: list[str] | None = None,
    ) -> PromptArtifact:
        context = self.context_composer.compose(
            artifacts=artifacts,
            constraints=constraints,
        )

        contract = PromptContract(
            context=context,
            role=role,
            instruction=instruction,
            examples=examples or [],
            borders=constraints,
        )

        optimized = self.prompt_doctor.optimize(contract)

        return PromptArtifact.from_contract(
            task_id=task_id,
            agent_id=agent_id,
            contract=optimized,
        )
