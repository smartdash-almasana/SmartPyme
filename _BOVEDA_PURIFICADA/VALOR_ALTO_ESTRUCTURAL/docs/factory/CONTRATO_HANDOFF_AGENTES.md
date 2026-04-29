---
status: CANONICO_PURIFICADO v1.1
created: 2026-04-28
purified: 2026-04-29
standard: SME_OS
validates_with:
  - _BOVEDA_PURIFICADA/VALOR_ALTO_ESTRUCTURAL/factory/ai_governance/contracts/verdict_enum.yaml
  - factory/ai_governance/schemas/agent_handoff.schema.json
  - factory/ai_governance/schemas/task_result.schema.json
  - factory/ai_governance/schemas/audit_result.schema.json
---

# Contrato de Handoff entre Agentes — SmartPyme Factory / SME OS

## Propósito

Este contrato define cómo se transfiere una unidad de trabajo entre Hermes Gateway, Codex, Gemini y ChatGPT sin ambigüedad de roles, estados ni evidencia.

SmartPyme es un SME OS. No admite entidades operativas huérfanas ni entregas sin soberanía de datos. Toda unidad de trabajo debe preservar `cliente_id` como ancla de identidad del sistema.

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

## Veredictos canónicos de handoff

Los estados legacy quedan reemplazados por el vocabulario de `_BOVEDA_PURIFICADA/VALOR_ALTO_ESTRUCTURAL/factory/ai_governance/contracts/verdict_enum.yaml`.

| Veredicto | Significado operacional |
|---|---|
| `SUCCESS_CODE` | Código generado y validado sintácticamente. |
| `SUCCESS_FACTORY` | Módulo SaaS listo para integración en Core. |
| `VALIDATED_ARCH` | La propuesta respeta el Editorial Monolith y Sacred Modernism. |
| `BLOCKED_MISSING_ASSET` | Falta un archivo o contrato referenciado en el índice. |
| `BLOCKED_AMBIGUOUS_SPEC` | La TaskSpec contiene instrucciones contradictorias o vagas. |
| `BLOCKED_IDENTIDAD_CONFLICT` | Se detectó uso de `tenant_id` o falta `cliente_id`. |
| `REJECTED_STACK` | La propuesta usa tecnologías fuera del stack permitido. |
| `REJECTED_INFERENCE` | El agente propuso lógica basada en documentos conceptuales. |
| `REJECTED_SECURITY` | El código vulnera aislamiento de datos entre clientes. |
| `FAILED_LINT` | El código no pasa validación de PEP8 o tipos. |
| `FAILED_RUNTIME` | Error en dry-run del módulo. |

## Payload Hermes → Codex

Debe cumplir `factory/ai_governance/schemas/agent_handoff.schema.json`.

Campos mínimos:

```json
{
  "task_id": "string",
  "repo_ref": "main|commit_sha|branch",
  "source_agent": "hermes_gateway",
  "target_agent": "codex_builder",
  "verdict": "BLOCKED_MISSING_ASSET|BLOCKED_AMBIGUOUS_SPEC|SUCCESS_CODE|FAILED_RUNTIME",
  "allowed_files": ["path"],
  "forbidden_files": ["path"],
  "required_tests": ["command"],
  "evidence_path": "factory/evidence/<task_id>",
  "context_files": ["path"],
  "cliente_id": "string"
}
```

## Payload Codex → Hermes/Gemini

Debe cumplir `factory/ai_governance/schemas/task_result.schema.json`.

Incluye:

- `task_id`
- `agent_id`
- `verdict`
- `cliente_id`
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
- `verdict`
- `cliente_id`
- `audit_verdict`
- `violations`
- `evidence_reviewed`
- `required_fixes`
- `risk_level`

## Protocolo de Rechazo por Identidad

Cualquier entrega que no incluya el campo `cliente_id` o que haga referencia a `tenant_id` debe ser rechazada con el veredicto `BLOCKED_IDENTIDAD_CONFLICT`.

Esta regla aplica a:

- TaskSpecs;
- payloads Hermes → Codex;
- payloads Codex → Gemini;
- payloads Gemini → ChatGPT;
- modelos Pydantic;
- tablas SQL;
- repositorios de persistencia;
- documentación contractual nueva.

No se acepta una entidad operativa huérfana en el SME OS.

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

- Si Codex toca archivos fuera de `allowed_files`, veredicto `FAILED_RUNTIME` o `BLOCKED_AMBIGUOUS_SPEC`.
- Si faltan tests requeridos, veredicto `BLOCKED_MISSING_ASSET`.
- Si Gemini no puede verificar evidencia, veredicto `BLOCKED_MISSING_ASSET`.
- Si ChatGPT no puede leer evidencia reproducible, veredicto `BLOCKED_MISSING_ASSET`.
- Si aparece runner legacy activo, veredicto `REJECTED_STACK`.
- Si aparece `tenant_id` o falta `cliente_id`, veredicto `BLOCKED_IDENTIDAD_CONFLICT`.

## Referencias

- `docs/factory/RUNTIME_VIGENTE.md`
- `docs/factory/FACTORY_CONTRATO_OPERATIVO.md`
- `_BOVEDA_PURIFICADA/VALOR_ALTO_ESTRUCTURAL/factory/ai_governance/contracts/verdict_enum.yaml`
- `factory/ai_governance/schemas/agent_handoff.schema.json`
- `factory/ai_governance/schemas/task_result.schema.json`
- `factory/ai_governance/schemas/audit_result.schema.json`
- `factory/ai_governance/taskspec.schema.json`

## Historial de Cambios

- 2026-04-28 — Creado por remediación P1/P2 para cerrar F-012 y F-029.
- 2026-04-29 — Purificado para SME OS: estados legacy reemplazados por veredictos canónicos e inyección obligatoria de soberanía `cliente_id`.
