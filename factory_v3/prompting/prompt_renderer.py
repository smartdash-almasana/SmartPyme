from __future__ import annotations

from factory_v3.prompting.prompt_artifact import PromptArtifact


class PromptRenderer:
    def render(self, artifact: PromptArtifact) -> str:
        return artifact.rendered_prompt
