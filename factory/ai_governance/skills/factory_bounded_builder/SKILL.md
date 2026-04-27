# Skill: factory_bounded_builder

## Purpose

Ejecutar una TaskSpec de SmartPyme Factory con margen de acción mínimo.

## Mandatory Inputs

- TaskSpec YAML
- repo_root
- allowed_files
- locked_files
- required_tests

## Procedure

1. Read TaskSpec.
2. Run preflight commands.
3. Verify no locked file will be modified.
4. Apply changes only to allowed_files.
5. Run required_tests.
6. Emit BuildReport.

## Refusal / Block Conditions

Return BLOCKED if:
- required change touches a locked file
- required change touches a forbidden file
- tests cannot be run
- TaskSpec is missing required fields

## Output

VEREDICTO_BUILDER
FILES_TOUCHED
COMMANDS_RUN
TEST_RESULT
EVIDENCE
GIT_STATUS
BLOCKERS
