# SmartPyme Target Architecture

## Purpose

This document describes the product horizon: the finished SmartPyme SaaS as a business operating system for PyMEs.

It is not a statement of current implementation. It is the target architecture that guides engineering direction.

## Product horizon

SmartPyme should become a sovereign operating layer between the owner and the scattered reality of the business.

It receives demand, interprets it, requests evidence, investigates, diagnoses, proposes, and waits for owner confirmation before action.

## Target system map

```text
Owner
  -> Hermes Runtime
  -> AI Intake / Pydantic AI
  -> SoftInterpretationResult
  -> Deterministic Core
  -> Variables / Evidence / Catalogues
  -> Investigation / Jobs
  -> Findings / Diagnosis / Proposals
  -> Owner confirmation
  -> Controlled action
```

## Target layers

### Owner Layer

The owner is sovereign.

Responsibilities:

- express demand
- clarify context
- authorize investigation
- upload or connect evidence
- confirm or reject proposals
- decide final actions

### Hermes Runtime

Hermes Runtime is the future product coordinator inside SmartPyme.

Responsibilities:

- receive owner messages
- coordinate conversational intake
- ask clarification questions
- call AI intake when useful
- route validated requests to deterministic boundaries
- preserve owner-confirmation rules

Status:

```text
conceptual / not yet a complete runtime module
```

### AI Layer

The AI Layer interprets language.

Responsibilities:

- produce provisional interpretation
- expose doubts
- produce validated structures
- fail safely

It must not:

- decide
- persist
- create jobs directly
- call pipeline directly
- produce final findings

### Hard Core

The deterministic core owns business truth.

Responsibilities:

- contracts
- validation
- calculations
- reconciliation
- canonical entities
- findings
- evidence-backed diagnosis

### Evidence Layer

The Evidence Layer should manage files, messages, documents, tables and external sources.

Target responsibilities:

- register evidence
- preserve provenance
- extract facts
- link facts to entities
- support source comparison
- support auditability

### Jobs Layer

Jobs should orchestrate long-running investigation work.

Target responsibilities:

- hold task state
- support retries
- preserve cliente_id isolation
- coordinate investigation steps
- never imply final decision by itself

### Catalogues

Catalogues are operational memory.

Target catalogues:

- PyME taxonomy
- business pathologies
- required variables
- expected evidence
- formulas and algorithms
- owner policies
- external market references

### External Context / Deep Search

The finished product may include authorized external investigation.

Potential sources:

- market prices
- supplier alternatives
- competitor signals
- regulatory changes
- local opportunities

Boundary:

```text
External context informs proposals. It is not internal business truth.
```

## Target flow

```text
1. Owner sends a message.
2. Hermes Runtime receives it.
3. AI Intake interprets language into a validated soft result.
4. Runtime checks whether context is sufficient.
5. Core determines required variables and evidence.
6. Owner authorizes investigation or uploads evidence.
7. Jobs coordinate investigation.
8. Evidence is processed into facts.
9. Core compares sources and detects findings.
10. System presents diagnosis and proposals.
11. Owner confirms, rejects or corrects.
12. Controlled action may be generated only after authorization.
```

## Target anti-risk principles

| Risk | Control |
|---|---|
| LLM hallucination | Pydantic validation plus deterministic core |
| Premature automation | Owner confirmation boundary |
| Wrong branch or construction confusion | Active branch docs and Hermes Factory vs Runtime doc |
| Data leakage | `cliente_id` isolation |
| Unsupported diagnosis | Evidence requirement |
| Generic advice | Taxonomy and catalogues |
| Connector coupling | Plugin boundary |
| Future confusion | Implementation status matrix |

## What production means

SmartPyme is production-ready only when:

- owner intake is integrated with Hermes Runtime
- AI Layer remains isolated and tested
- deterministic core validates all business facts
- evidence provenance is preserved
- jobs can recover and report state
- findings cite evidence
- owner confirmation is enforced
- cliente_id isolation is verified end-to-end
- product UX makes uncertainty visible

## Engineering direction

Near-term path:

```text
AI intake boundary -> Hermes Runtime boundary -> context validation -> evidence request -> controlled job creation -> investigation -> findings -> owner confirmation
```

No step should skip the previous boundary.
