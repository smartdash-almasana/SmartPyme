# TS_016 Pydantic AI Interpreter Execution

## Purpose

Implement the first controlled use of Pydantic AI as a Soft Core interpreter for owner messages.

## Architectural role

This task belongs to the AI layer.
It does not modify the deterministic core.

## Files

```text
app/ai/schemas/owner_message_interpretation.py
app/ai/agents/owner_message_interpreter_agent.py
tests/ai/test_owner_message_interpreter_agent.py
```

## Contract

`OwnerMessageInterpretation` is the only validated output shape.

Fields:

- `intent: str | None`
- `entities: list[str]`
- `variables: list[str]`
- `evidence: list[str]`
- `doubts: list[str]`
- `confidence: float | None`

## Execution rule

The agent may call `pydantic_ai.Agent.run` only when:

- `pydantic_ai` is importable
- at least one supported API key exists
- agent construction succeeds

## Failure behavior

The public function must return `None` when:

- dependency is missing
- credentials are missing
- agent construction fails
- LLM execution fails
- output validation fails
- input message is empty

No exception should escape the AI boundary.

## Forbidden scope

TS_016 must not:

- modify pipeline
- modify `AnamnesisService`
- persist results
- create jobs
- use external data beyond the configured model call
- generate final findings
- decide actions

## Validation

```bash
pytest tests/ai/test_owner_message_interpreter_agent.py -q
```

## Integration status

Implemented but isolated.
No pipeline integration yet.
