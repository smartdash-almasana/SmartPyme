from __future__ import annotations

from pydantic import BaseModel

from factory_v3.prompting.prompt_artifact import PromptArtifact


class PromptEvaluation(BaseModel):
    score: float
    passed: bool
    feedback: str


class PromptEvaluator:
    def evaluate(self, artifact: PromptArtifact) -> PromptEvaluation:
        prompt_length = len(artifact.rendered_prompt)

        passed = prompt_length > 50
        score = min(prompt_length / 1000, 1.0)

        feedback = "prompt accepted" if passed else "prompt too short"

        return PromptEvaluation(
            score=score,
            passed=passed,
            feedback=feedback,
        )
