from __future__ import annotations

from factory_v3.prompting.prompt_contract import PromptContract


class PromptDoctor:
    def optimize(self, contract: PromptContract) -> PromptContract:
        borders = list(contract.borders)

        if "avoid ambiguity" not in borders:
            borders.append("avoid ambiguity")

        if "respect output schema" not in borders:
            borders.append("respect output schema")

        return PromptContract(
            context=contract.context,
            role=contract.role,
            instruction=contract.instruction,
            examples=contract.examples,
            borders=borders,
        )
