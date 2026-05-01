# TS_017 Local Soft Interpreter Adapter

## Purpose

Create a local adapter that wraps the Soft Core owner-message interpreter and exposes a stable local interface.

## Architectural role

This task belongs to the AI layer.
It is an adapter boundary, not a pipeline integration.

## Files

```text
app/ai/adapters/owner_message_interpreter_adapter.py
tests/ai/test_owner_message_interpreter_adapter.py
```

## Adapter

`LocalOwnerMessageInterpreterAdapter` receives an owner message and returns a validated `OwnerMessageInterpretation`.

It may use:

- the default `interpret_owner_message_with_ai`
- an injected interpreter for tests or local replacement

## Output rule

The adapter must always return a valid `OwnerMessageInterpretation`.

When the interpreter fails or returns no valid output, the adapter returns an empty interpretation:

```text
intent=None
entities=[]
variables=[]
evidence=[]
doubts=[]
confidence=None
```

## Failure behavior

The adapter returns the empty interpretation when:

- message is empty
- interpreter returns `None`
- interpreter raises
- interpreter returns raw unvalidated output

## Forbidden scope

TS_017 must not:

- modify pipeline
- modify deterministic services
- persist output
- create jobs
- make business decisions
- confirm context

## Validation

```bash
pytest tests/ai/test_owner_message_interpreter_adapter.py -q
```

Recommended combined validation:

```bash
pytest tests/ai/test_owner_message_interpreter_agent.py tests/ai/test_owner_message_interpreter_adapter.py -q
```

## Integration status

Implemented but isolated.
This adapter prepares a future stable integration boundary.

Recommended next task:

```text
TS_018 SoftInterpretationResult contract
```
