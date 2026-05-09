from factory_v3.prompting.prompt_builder import PromptBuilder
from factory_v3.prompting.prompt_evaluator import PromptEvaluator
from factory_v3.prompting.prompt_versioning import PromptVersioner


def test_prompt_governance_pipeline_builds_versions_and_evaluates():
    builder = PromptBuilder()

    artifact = builder.build(
        task_id="task-1",
        agent_id="architect-agent",
        role="architect",
        instruction="Design a durable runtime architecture.",
        artifacts=["Artifact ledger specification"],
        constraints=["respect output schema"],
        examples=["Example runtime design"],
    )

    versioner = PromptVersioner()
    version = versioner.create_version(artifact)

    evaluator = PromptEvaluator()
    evaluation = evaluator.evaluate(artifact)

    assert artifact.rendered_prompt
    assert version.prompt_hash
    assert evaluation.passed is True
