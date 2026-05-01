# AI Layer Architecture

## Status

Implemented on the active branch:

```text
factory/ts-006-jobs-sovereign-persistence
```

The AI layer is isolated under:

```text
app/ai/
```

It is a Soft Core boundary. It does not own business truth.

## System rule

```text
The LLM interprets.
Pydantic validates.
The deterministic core processes.
The owner confirms.
```

## Current files

```text
app/ai/schemas/owner_message_interpretation.py
app/ai/schemas/soft_interpretation_result.py
app/ai/agents/owner_message_interpreter_agent.py
app/ai/adapters/owner_message_interpreter_adapter.py
app/ai/consumers/owner_message_soft_interpretation_consumer.py
```

## Responsibility

The AI layer may:

- interpret an owner message
- extract provisional intent
- extract provisional entities
- extract provisional variables
- extract mentioned evidence
- expose doubts or missing context
- return a validated empty result when interpretation is unavailable
- consume a soft interpretation result inside the AI boundary

The AI layer must not:

- modify pipeline state
- persist interpretations
- create jobs
- generate final findings
- confirm operational context
- decide actions
- bypass owner confirmation

## Contracts

### OwnerMessageInterpretation

Primary normalized fields:

```text
intent
entities
variables
evidence
doubts
confidence
```

Backward-compatible TS_015 fields:

```text
rubro_posible
dolores_detectados
fuentes_mencionadas
datos_mencionados
hipotesis_sistema
preguntas_sugeridas
nivel_confianza
necesita_confirmacion
```

The compatibility fields remain because the active branch still contains scaffold tests that depend on them.

### SoftInterpretationResult

Stable adapter and consumer result:

```text
raw_message
interpretation
status: ok | empty | failed
source: local_adapter
errors
```

This contract prepares future consumers without requiring direct dependency on an LLM provider.

## Agent boundary

`owner_message_interpreter_agent.py` must be defensive.

It returns `None` when:

- `pydantic_ai` is unavailable
- no supported API key exists
- agent construction fails
- model execution fails
- model output does not validate
- the input message is empty

Compatibility aliases are intentionally kept:

```text
HAS_PYDANTIC_AI
build_owner_message_interpreter_agent()
```

## Adapter boundary

`LocalOwnerMessageInterpreterAdapter` exposes:

```text
interpret(message) -> OwnerMessageInterpretation
interpret_result(message) -> SoftInterpretationResult
```

`interpret()` is compatibility-oriented.
`interpret_result()` is the preferred future integration surface.

## Consumer boundary

`OwnerMessageSoftInterpretationConsumer` is the first internal consumer of `SoftInterpretationResult`.

It exposes:

```text
consume(message) -> SoftInterpretationResult
```

The consumer may normalize adapter failures into `failed` results.
It may return `empty` for blank messages.
It must not persist, create jobs, call pipeline, confirm context, or decide actions.

## Integration status

Current status:

```text
Implemented but isolated.
```

Not yet connected to:

- pipeline
- jobs
- persistence
- owner confirmation flow

## Validation

```bash
pytest tests/ai -q
```

Expected state after TS_022:

```text
tests/ai PASS
no runtime code modified
```
