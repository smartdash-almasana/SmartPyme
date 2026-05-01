# TS_016-019 AI Layer Technical Record

## Active branch

```text
factory/ts-006-jobs-sovereign-persistence
```

Do not recreate this work from `main`.

## Purpose

Introduce an isolated Soft Core AI layer for owner-message interpretation.

This layer prepares future conversational intake without changing deterministic core behavior.

## Implemented tasks

### TS_016 Pydantic AI interpreter execution

Adds defensive Pydantic AI integration.

Main file:

```text
app/ai/agents/owner_message_interpreter_agent.py
```

Public functions:

```text
create_owner_message_interpreter_agent()
interpret_owner_message_with_ai_async()
interpret_owner_message_with_ai()
build_owner_message_interpreter_agent()
```

Compatibility constant:

```text
HAS_PYDANTIC_AI
```

Failure behavior:

```text
return None
```

### TS_017 Local soft interpreter adapter

Adds a local adapter boundary.

Main file:

```text
app/ai/adapters/owner_message_interpreter_adapter.py
```

Public API:

```text
LocalOwnerMessageInterpreterAdapter.interpret()
LocalOwnerMessageInterpreterAdapter.interpret_result()
```

### TS_018 Soft interpretation result contract

Adds a stable result wrapper.

Main file:

```text
app/ai/schemas/soft_interpretation_result.py
```

Status values:

```text
ok
empty
failed
```

Source value:

```text
local_adapter
```

### TS_019 Adapter result contract

Makes the adapter expose `SoftInterpretationResult` while preserving the previous interpretation-only API.

## Compatibility decision

The active branch contains earlier TS_015 scaffold tests.
Therefore `OwnerMessageInterpretation` intentionally supports both normalized and legacy fields.

Normalized fields:

```text
intent
entities
variables
evidence
doubts
confidence
```

Legacy scaffold fields:

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

`nivel_confianza` defaults to `0.0` for compatibility.

## Forbidden scope

These tasks must not:

- modify pipeline
- modify jobs
- persist AI output
- create findings
- confirm operational context
- decide actions
- call external data sources outside the configured model provider

## Test coverage

```text
tests/ai/test_owner_message_interpretation_schema.py
tests/ai/test_owner_message_interpreter_agent.py
tests/ai/test_owner_message_interpreter_adapter.py
tests/ai/test_soft_interpretation_result.py
```

## Validation command

```bash
pytest tests/ai -q
```

Expected result:

```text
PASS
```

## Future next step

Recommended next task:

```text
TS_021 first internal consumer of SoftInterpretationResult
```

Scope restriction for TS_021:

```text
No pipeline integration yet.
No persistence.
No jobs.
```
