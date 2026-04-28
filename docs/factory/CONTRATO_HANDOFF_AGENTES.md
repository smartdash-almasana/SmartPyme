---
status: CANONICO v1
created: 2026-04-28
replaces:
  - F-012
  - F-029
validates_with: test -f docs/factory/CONTRATO_HANDOFF_AGENTES.md && test -f factory/ai_governance/schemas/agent_handoff.schema.json
---

# Contrato de Handoff entre Agentes — SmartPyme Factory

## Propósito

Este contrato define cómo se transfiere una unidad de trabajo entre Hermes Gateway, Codex, Gemini y ChatGPT sin ambigüedad de roles, estados ni evidencia.

SmartPyme no ejecuta una factoría autónoma dentro del repo. El repo contiene contratos, TaskSpecs, gates y evidencia. La ejecución ocurre por agentes externos gobernados.

## Flujo vigente

```text
Owner Telegram
→ Hermes Gateway externo
→ factory/hermes_control_cli.py
→ TaskSpec YAML
→ Codex Builder externo
→ Gemini Auditor externo
→ ChatGPT Director/Auditor externo
→ decisión humana / gate
```

## Roles

| Agente | Rol | Puede | No puede |
|---|---|---|---|
| Hermes Gateway | Orquestador conversacional externo | Leer gate, tomar una TaskSpec, invocar adaptadores, registrar evidencia | Validar su propio trabajo, ejecutar runners legacy |
| Codex | Builder externo | Modificar archivos permitidos por TaskSpec, ejecutar tests, emitir build report | Decidir arquitectura final, auditarse a sí mismo |
| Gemini | Auditor técnico externo | Revisar diff, evidencia, tests y contratos | Ser Builder productivo por defecto |
| ChatGPT | Director/Auditor externo | Auditar evidencia, decidir próximo paso, redactar TaskSpecs | Ejecutar ciclos autónomos sin evidencia |

## Unidad de trabajo

La unidad de trabajo vigente es una TaskSpec YAML en:

```text
factory/ai_governance/tasks/*.yaml
```

El modelo `factory/hallazgos/<state>/*.md` queda como antecedente histórico o dominio de negocio, no como cola activa de factoría.

## Estados de handoff

| Estado | Significado |
|---|---|
| `PENDING` | TaskSpec disponible, no tomada. |
| `IN_PROGRESS` | Agente ejecutor tomó la unidad. |
| `BUILD_SUCCESS` | Codex completó cambios y pruebas mínimas. |
| `BUILD_FAILED` | Codex falló en build/test. |
| `BUILD_BLOCKED` | Codex no puede avanzar por falta de contexto, permisos o entorno. |
| `AUDIT_PASSED` | Gemini validó evidencia técnica. |
| `AUDIT_REJECTED` | Gemini encontró violación de contrato. |
| `AUDIT_BLOCKED` | Gemini no puede auditar por falta de evidencia. |
| `WAITING_AUDIT` | El ciclo espera auditoría externa o humana. |
| `APPROVED` | ChatGPT/Owner aprueba con evidencia. |
| `REJECTED` | ChatGPT/Owner rechaza por incumplimiento. |
| `BLOCKED` | El gate queda bloqueado hasta corrección explícita. |
| `NEEDS_REVIEW` | Requiere revisión humana antes de continuar. |

## Payload Hermes → Codex

Debe cumplir `factory/ai_governance/schemas/agent_handoff.schema.json`.

Campos mínimos:

```json
{
  "task_id": "string",
  "repo_ref": "main|commit_sha|branch",
  "source_agent": "hermes_gateway",
  "target_agent": "codex_builder",
  "status": "PENDING",
  "allowed_files": ["path"],
  "forbidden_files": ["path"],
  "required_tests": ["command"],
  "evidence_path": "factory/evidence/<task_id>",
  "context_files": ["path"]
}
```

## Payload Codex → Hermes/Gemini

Debe cumplir `factory/ai_governance/schemas/task_result.schema.json`.

Incluye:

- `task_id`
- `agent_id`
- `status`
- `files_changed`
- `commands_run`
- `tests_result`
- `evidence_path`
- `blockers`
- `commit_sha`, si hubo commit

## Payload Gemini → Hermes/ChatGPT

Debe cumplir `factory/ai_governance/schemas/audit_result.schema.json`.

Incluye:

- `task_id`
- `agent_id`
- `status`
- `audit_verdict`
- `violations`
- `evidence_reviewed`
- `required_fixes`
- `risk_level`

## Ownership de evidencia

| Evidencia | Responsable |
|---|---|
| TaskSpec original | Hermes Gateway / repo |
| Build output | Codex |
| Tests y comandos | Codex |
| Audit report | Gemini |
| Dictamen final | ChatGPT / Owner |
| Gate final | Hermes Gateway bajo decisión humana |

Toda evidencia debe vivir bajo:

```text
factory/evidence/<task_id>/
```

## Rollback y errores

- Si Codex toca archivos fuera de `allowed_files`, estado `BUILD_FAILED` o `BUILD_BLOCKED`.
- Si faltan tests requeridos, estado `BUILD_BLOCKED`.
- Si Gemini no puede verificar evidencia, estado `AUDIT_BLOCKED`.
- Si ChatGPT no puede leer evidencia reproducible, decisión `NO_VALIDADO` o `BLOCKED` según contrato vigente.
- Si aparece runner legacy activo, el ciclo queda `BLOCKED`.

## Referencias

- `docs/factory/RUNTIME_VIGENTE.md`
- `docs/factory/FACTORY_CONTRATO_OPERATIVO.md`
- `factory/ai_governance/contracts/verdict_enum.yaml`
- `factory/ai_governance/taskspec.schema.json`

## Historial de Cambios

- 2026-04-28 — Creado por remediación P1/P2 para cerrar F-012 y F-029. Define handoff Hermes → Codex → Gemini → ChatGPT con ownership de evidencia y estados normalizados.
