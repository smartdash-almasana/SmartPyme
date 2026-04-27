# Skill: factory_auditor

## Purpose

Auditar una ejecución de Builder sin modificar código.

## Inputs

- TaskSpec
- git diff
- BuildReport
- test output
- git status

## Rules

Reject if:
- forbidden/locked files were touched
- tests were not run
- evidence missing
- schema changed without governance TaskSpec
- tests were rewritten to match degraded behavior

## Output

AuditReport:
- verdict
- reason
- scope_violations
- contract_violations
- tests_verified
- evidence_verified
- next_minimal_fix
