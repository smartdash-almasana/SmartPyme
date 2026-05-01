# AI Layer Architecture

The AI layer is a Soft Core boundary.

It exists to interpret owner messages and produce structured, validated, provisional outputs.
It does not own business truth.

## Current implementation

```text
app/ai/
  schemas/
    owner_message_interpretation.py
  agents/
    owner_message_interpreter_agent.py
  adapters/
    owner_message_interpreter_adapter.py
```

## Responsibility

The AI layer may:

- interpret an owner message
- extract provisional intent
- extract provisional entities
- extract provisional variables
- extract mentioned evidence
- expose doubts or missing context

The AI layer must not:

- modify pipeline state
- persist interpretations
- create jobs
- generate final findings
- confirm context
- decide actions
- bypass owner confirmation

## TS_016 boundary

`OwnerMessageInterpreterAgent` integrates with `pydantic_ai` only when available.

Failure modes must return `None`:

- dependency not installed
- missing API key
- agent creation failure
- model execution failure
- invalid model output

## TS_017 boundary

`LocalOwnerMessageInterpreterAdapter` wraps the soft interpreter and normalizes output.

It returns:

- a validated `OwnerMessageInterpretation` when the soft interpreter succeeds
- an empty validated `OwnerMessageInterpretation` when the soft interpreter fails

This makes the future consumer independent from provider failures.

## Validation rule

No raw model output may cross the AI boundary.

Allowed external output:

```text
OwnerMessageInterpretation | validated empty OwnerMessageInterpretation
```

## Future integration rule

Before the pipeline consumes AI output, a dedicated result contract should be introduced.

Recommended next contract:

```text
SoftInterpretationResult
  raw_message: str
  interpretation: OwnerMessageInterpretation
  status: ok | empty | failed
  source: local_adapter
  errors: list[str]
```

This contract should be added before any pipeline integration.
