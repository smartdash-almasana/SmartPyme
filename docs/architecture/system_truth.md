# SmartPyme System Truth

SmartPyme is a business operating system for small and medium businesses.
It is not a traditional CRUD application and it is not an autonomous decision system.

## Central rule

SmartPyme does not decide.
SmartPyme proposes.
The owner confirms.

## Operating flow

```text
reception
-> classification
-> pyme taxonomy
-> required variables
-> evidence
-> investigation
-> diagnosis
-> proposals
-> owner decision
```

## Engineering doctrine

Every relevant output must preserve:

- explicit business entity
- quantified difference when applicable
- compared sources when applicable
- evidence path or evidence reference
- owner-confirmation boundary

## Non-negotiable boundaries

- The deterministic core owns contracts, validation, calculation and persistence.
- The AI layer may interpret, summarize and hypothesize.
- The owner layer confirms, corrects and prioritizes.
- No LLM output is a source of truth until validated and confirmed.

## Naming doctrine

Preferred domain language:

- `cliente_id`, never `tenant_id`
- `hallazgo`, not generic `finding` in product language
- `evidencia`, not opaque untrusted input
- `entidad`, not generic record
- `propuesta`, not automatic action

## System invariant

```text
LLM interpretation is provisional.
Pydantic validation is structural.
Core processing is deterministic.
Owner confirmation is sovereign.
```
