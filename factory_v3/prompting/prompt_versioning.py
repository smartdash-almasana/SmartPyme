from __future__ import annotations

from hashlib import sha256

from pydantic import BaseModel, Field

from factory_v3.prompting.prompt_artifact import PromptArtifact


class PromptVersion(BaseModel):
    version_id: str
    task_id: str
    agent_id: str
    prompt_hash: str
    rendered_prompt: str
    metadata: dict = Field(default_factory=dict)


class PromptVersioner:
    def create_version(self, artifact: PromptArtifact) -> PromptVersion:
        prompt_hash = sha256(artifact.rendered_prompt.encode("utf-8")).hexdigest()

        return PromptVersion(
            version_id=prompt_hash[:16],
            task_id=artifact.task_id,
            agent_id=artifact.agent_id,
            prompt_hash=prompt_hash,
            rendered_prompt=artifact.rendered_prompt,
        )
