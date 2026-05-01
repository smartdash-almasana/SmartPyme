# Hermes Factory vs Hermes Runtime Boundary

## Purpose

This document prevents a critical naming collision.

SmartPyme uses the name Hermes in two different architectural contexts:

```text
Hermes Factory != Hermes Runtime
```

They must not be treated as the same component.

## Hermes Factory

Hermes Factory is part of the construction system.

It exists to help build SmartPyme.

Responsibilities:

- coordinate development agents
- receive and execute engineering tasks
- apply repository changes
- validate task outputs
- record evidence
- support the multi-agent factory loop

Typical location:

```text
factory/
docs/factory/
external runner or factory environment
```

Hermes Factory is not product runtime.
It should not be imported by runtime modules under `app/**`.

## Hermes Runtime

Hermes Runtime is a product concept inside SmartPyme.

It exists to operate inside the SME OS.

Responsibilities:

- receive owner messages
- coordinate conversational intake
- ask clarification questions
- route demand to internal modules
- coordinate soft interpretation with deterministic validation
- preserve owner-confirmation boundaries

Expected product location:

```text
app/
app/ai/
app/services/
app/core/
```

Hermes Runtime may use AI-layer components, but it must not bypass deterministic validation or owner confirmation.

## Pydantic AI relationship

Pydantic AI belongs to the SmartPyme runtime layer.

It may be used by Hermes Runtime as a soft interpreter.

Correct relationship:

```text
Hermes Runtime
-> OwnerMessageSoftInterpretationConsumer
-> SoftInterpretationResult
-> deterministic core boundary
-> owner confirmation
```

Incorrect relationship:

```text
Hermes Factory
-> app/ai runtime calls
-> business interpretation
```

Hermes Factory may help create or test `app/ai/**`, but it is not part of the product execution path.

## Boundary rule

```text
Hermes Factory builds SmartPyme.
Hermes Runtime operates inside SmartPyme.
Pydantic AI interprets for Hermes Runtime.
The deterministic core validates and computes.
The owner confirms.
```

## Forbidden coupling

Do not:

- import factory code from `app/**`
- call Hermes Factory from runtime product modules
- let Pydantic AI create factory tasks
- let Hermes Factory become a business runtime dependency
- let Hermes Runtime mutate repository or factory state
- let any Hermes component decide on behalf of the owner

## Naming recommendation

When writing docs, prompts, code comments, or task descriptions, use explicit names:

```text
Hermes Factory
Hermes Runtime
```

Avoid the unqualified term `Hermes` when the context is ambiguous.

## Current implementation status

Implemented now:

```text
app/ai/**
```

Not implemented yet:

```text
Hermes Runtime product module
```

The current AI Layer is a prerequisite for Hermes Runtime, not Hermes Runtime itself.

## Next engineering implication

Before implementing Hermes Runtime, create an explicit runtime boundary module and keep it separate from factory infrastructure.

Recommended future task:

```text
TS_023 local orchestration boundary for AI intake
```

Scope restriction:

```text
No factory imports.
No pipeline integration yet.
No persistence.
No jobs.
```
