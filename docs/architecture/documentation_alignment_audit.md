# Documentation Alignment Audit

## Verdict

The repository contains useful operational traces, but it needs a stable architecture documentation layer.

This document establishes the alignment rule:

```text
factory/evidence/** = execution traces
PR descriptions = task records
docs/** = stable architecture truth
```

## Current problem

Before this documentation block, engineering knowledge was spread across:

- task prompts
- PR descriptions
- factory evidence
- chat context
- implementation files

That makes execution possible but weakens architectural continuity.

## Required documentation standard

Every major task must be documented with:

1. task id
2. architectural purpose
3. files touched
4. allowed scope
5. forbidden scope
6. contracts introduced or modified
7. failure behavior
8. validation command
9. integration status

## Alignment matrix

| Area | Current state | Required standard |
|---|---|---|
| Product doctrine | Exists in concept docs | Mirror stable rules in `docs/architecture` |
| Engineering tasks | Exists in PRs/evidence | Add stable docs under `docs/technical` |
| AI boundary | Implemented in code | Documented in `docs/architecture/ai_layer.md` |
| Core boundary | Partially implicit | Keep explicit in `hard_soft_owner_layers.md` |
| Owner authority | Clear conceptually | Keep as invariant in all architecture docs |

## Documentation anti-patterns

Avoid:

- treating evidence logs as canonical architecture docs
- placing long theory inside code comments
- documenting tasks only in chats
- mixing product doctrine with implementation details
- documenting LLM behavior as deterministic behavior

## Engineering rule

A future builder must be able to answer these questions from `docs/**` without reading chats:

- What is SmartPyme allowed to decide?
- What belongs to Hard Core?
- What belongs to Soft Core?
- What does the owner confirm?
- What can the AI layer return?
- What must never be persisted without confirmation?

## Immediate alignment result

This branch adds the first stable architecture layer:

- `docs/README.md`
- `docs/architecture/system_truth.md`
- `docs/architecture/hard_soft_owner_layers.md`
- `docs/architecture/ai_layer.md`
- `docs/architecture/documentation_alignment_audit.md`
- `docs/technical/ts_016_pydantic_ai_interpreter.md`
- `docs/technical/ts_017_local_soft_interpreter_adapter.md`
