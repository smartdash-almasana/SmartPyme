# Implementation Status Matrix

## Purpose

This matrix prevents false certainty.

Every agent must distinguish current implementation from product horizon.

Status values:

```text
implemented
partial
documented
conceptual
future_target
unknown
```

## Matrix

| Component | Status | Evidence area | Can be used today | Do not assume |
|---|---|---|---|---|
| Active branch guard | implemented | `docs/ACTIVE_BRANCH.md` | yes | work from `main` |
| AI Layer | implemented isolated | `app/ai/**`, `tests/ai/**` | yes | pipeline integration |
| OwnerMessageInterpretation | implemented | `app/ai/schemas/**` | yes | final business truth |
| OwnerMessageInterpreterAgent | implemented defensive | `app/ai/agents/**` | yes with dependency limits | guaranteed LLM availability |
| LocalOwnerMessageInterpreterAdapter | implemented | `app/ai/adapters/**` | yes | persistence or jobs |
| SoftInterpretationResult | implemented | `app/ai/schemas/**` | yes | diagnosis by itself |
| OwnerMessageSoftInterpretationConsumer | implemented | `app/ai/consumers/**` | yes | pipeline call |
| AIIntakeOrchestrator | pending PR | `app/ai/orchestrators/**` | only after TS_023 merge | Hermes Runtime completeness |
| Hermes Factory | external/factory concept | `factory/**`, docs | yes for construction | product runtime dependency |
| Hermes Runtime | conceptual | architecture docs | no | implemented module |
| Hard Core | partial | `app/core/**`, `app/services/**` | verify per service | full end-to-end readiness |
| Jobs | partial | repositories/services/tests | verify per branch | automatic business execution |
| Pipeline | partial | `app/core/pipeline.py` if present | verify before use | AI intake integration |
| Repositories | partial | `app/repositories/**` | verify per repository | complete multi-tenant coverage |
| Evidence Layer | partial/conceptual | docs and code if present | verify per file | complete provenance loop |
| Catalogues | conceptual/partial | docs and code if present | limited | full operational knowledge base |
| External context / Deep Search | future_target | conceptual docs | no | production external search |
| Action execution | future_target/unknown | verify repo | no unless proven | autonomous actions |
| Owner confirmation | partial/documented | contracts/services/docs | verify flow | universal enforcement |

## Anti-assumption rules

An agent must not say a component is implemented because it is described in documentation.

An agent must not say a component is integrated because it has tests.

An agent must not say a component is production-ready because it exists as a file.

Use these distinctions:

```text
exists as file
has tests
is integrated
is exposed
is persistent
is production-ready
```

## Current safest statement

The safest current statement is:

```text
SmartPyme has an implemented and tested isolated AI intake layer.
It has a documented product horizon for Hermes Runtime and full SME OS operation.
The full end-to-end SaaS flow is not yet closed.
```

## Required citation style for future reports

When explaining SmartPyme, cite or name:

- file path
- component
- status
- limitation

Example:

```text
AI Layer: implemented isolated in app/ai/**. It returns SoftInterpretationResult, but it is not integrated with pipeline or jobs yet.
```

## Next update rule

Whenever a task merges, update this matrix if it changes:

- status
- evidence area
- integration boundary
- production assumption
