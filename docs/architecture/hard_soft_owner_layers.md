# Hard Core, Soft Core and Owner Layer

SmartPyme is split into three architectural responsibility layers.

## 1. Hard Core

The Hard Core is deterministic.

It owns:

- contracts
- catalogues
- validation
- calculation
- comparison
- persistence
- access isolation by `cliente_id`

It must not depend on LLM availability.
It must not call external model providers directly.
It must not accept unvalidated AI output as business truth.

## 2. Soft Core

The Soft Core is interpretive.

It may perform:

- message interpretation
- hypothesis generation
- ambiguity detection
- summarization
- candidate extraction
- soft classification

It must return validated structures.
It must tolerate failure.
It must have safe empty fallbacks.
It must never persist by itself.

## 3. Owner Layer

The Owner Layer is sovereign.

It owns:

- confirmation
- correction
- prioritization
- final authorization
- operational decision

The system may ask questions.
The system may propose actions.
The owner decides.

## Boundary table

| Responsibility | Hard Core | Soft Core | Owner Layer |
|---|---:|---:|---:|
| Interpret natural language | No | Yes | Yes |
| Validate structure | Yes | Yes | No |
| Calculate differences | Yes | No | No |
| Persist business facts | Yes | No | No |
| Generate hypotheses | No | Yes | Yes |
| Confirm operational context | No | No | Yes |
| Decide action | No | No | Yes |

## Engineering test

A module belongs in the Soft Core if its failure can safely return an empty result without corrupting state.
A module belongs in the Hard Core if incorrect behavior can corrupt business truth, persistence or isolation.
