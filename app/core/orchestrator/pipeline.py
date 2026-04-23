from typing import Any, Callable

StepFn = Callable[[Any], Any]


def run_pipeline_flow(
    payload: list[dict[str, Any]],
    *,
    normalize: StepFn,
    match: StepFn,
    diff: StepFn,
    validation: StepFn,
    signals: StepFn,
) -> tuple[list[str], Any]:
    steps_executed: list[str] = []

    normalized = normalize(payload)
    steps_executed.append("normalize")

    matched = match(normalized)
    steps_executed.append("match")

    differences = diff(matched)
    steps_executed.append("diff")

    validated = validation(differences)
    steps_executed.append("validation")

    signal_output = signals(validated)
    steps_executed.append("signals")

    return steps_executed, signal_output
