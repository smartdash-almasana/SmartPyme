# SmartPyme Storyroad & Traceability

## Purpose

This is the first reading document for any new agent, developer, or AI entering the repository.

It explains the road of the system:

```text
original business pain -> architectural decision -> risk controlled -> current implementation -> product horizon
```

## Product thesis

SmartPyme is a business operating system for small and medium businesses.

It is not an ERP, CRM, dashboard, or chatbot. It exists to help the owner convert scattered operational signals into structured understanding, evidence-backed diagnosis, proposals, and confirmed decisions.

## Sovereign rule

```text
SmartPyme does not decide.
SmartPyme proposes.
The owner confirms.
```

## Storyroad

| Step | System idea | Architectural decision | Risk controlled | Current state |
|---|---|---|---|---|
| 1 | PyME as organism | Model taxonomy, context, variables, evidence and findings | Generic software without business sense | Conceptual and partial implementation |
| 2 | Finding | Require entity, quantified difference, source comparison and evidence | Vague diagnosis | Partially implemented |
| 3 | Interpretation | Add Soft Core before deterministic core | Natural language contaminating hard contracts | Implemented in AI layer |
| 4 | Copilot | Generate questions and tasks, not final decisions | Uncontrolled automation | Conceptual and partial implementation |
| 5 | Modes/modules/nodes | Separate authorization, domain and execution | Mixed responsibilities | Conceptual |
| 6 | Sense manager | Connect data with meaning | Repository without diagnosis | Conceptual |
| 7 | Investigation | Require variables and evidence before diagnosis | Unsupported conclusions | Partial |
| 8 | Components/modules/plugins | Separate system capability, domain use and connector | Coupled integrations | Conceptual |
| 9 | Demand receiver | Receive incomplete owner messages before execution | Premature execution | Partially represented by AI layer |
| 10 | Catalogues | Reuse operational knowledge | Starting each case from zero | Conceptual and partial |
| 11 | Full flow | Reception to owner decision | Fragmented product logic | Documented |
| 12 | PyME taxonomy | Adapt questions and evidence by business type | Generic questioning | Partial |
| 13 | Variables/evidence | Match required variables with available evidence | Diagnosis without support | Partial |
| 14 | External context | Add market and supplier context with authorization | Internal-only diagnosis | Future target |

## Canonical flow

```text
reception -> classification -> taxonomy -> variables -> evidence -> investigation -> diagnosis -> proposals -> owner decision
```

## Traceability matrix

| Decision | Why it exists | Files or area | State | Do not assume |
|---|---|---|---|---|
| Soft Core vs Hard Core | Use AI without making AI the source of truth | `app/ai/**`, `app/core/**` | Partial | AI is not business truth |
| AI Layer isolation | Interpret owner messages safely | `app/ai/**` | Implemented isolated | No pipeline integration yet |
| Owner sovereignty | Keep decisions with the owner | docs and contracts | Documented | No autonomous final decision |
| Hermes Factory vs Runtime | Separate builder from product runtime | `docs/architecture/hermes_factory_vs_runtime.md` | Documented | Runtime module is not complete yet |
| Pydantic contracts | Validate soft outputs | `app/ai/schemas/**` | Implemented | Validation is not diagnosis |
| Evidence requirement | Ground findings in sources | docs and partial services | Partial | Do not assume full evidence loop |
| Catalogues | Encode reusable business knowledge | docs and partial code | Partial | Do not assume all catalogues are implemented |
| External context | Add market intelligence | conceptual docs | Future target | Not implemented as production feature |

## Reading rule

A new agent must distinguish:

```text
implemented != documented != conceptual != future target
```

If the state is unclear, mark it as uncertain instead of assuming it is implemented.

## Mandatory reading order

1. `docs/ACTIVE_BRANCH.md`
2. `docs/architecture/smartpyme_storyroad_traceability.md`
3. `docs/architecture/smartpyme_target_architecture.md`
4. `docs/architecture/implementation_status_matrix.md`
5. `docs/architecture/hermes_factory_vs_runtime.md`
6. `docs/architecture/ai_layer.md`
