---
status: CANONICO_PURIFICADO v2.0_HITL
created: 2026-04-28
purified: 2026-04-29
standard: SME_OS
validates_with:
  - _BOVEDA_PURIFICADA/VALOR_ALTO_ESTRUCTURAL/factory/ai_governance/contracts/verdict_enum.yaml
  - _BOVEDA_PURIFICADA/VALOR_ALTO_ESTRUCTURAL/factory/ai_governance/schemas/agent_handoff.schema.json
  - _BOVEDA_PURIFICADA/VALOR_ALTO_ESTRUCTURAL/factory/ai_governance/schemas/task_result.schema.json
  - _BOVEDA_PURIFICADA/VALOR_ALTO_ESTRUCTURAL/factory/ai_governance/schemas/audit_result.schema.json
---

# Contrato de Handoff entre Agentes — SmartPyme Factory / SME OS

## Propósito

Este contrato define cómo se transfiere una unidad de trabajo entre Hermes Gateway, Codex, Gemini y ChatGPT sin ambigüedad de roles, estados, evidencia ni autoridad de despliegue.

SmartPyme es un SME OS. No admite entidades operativas huérfanas ni entregas sin soberanía de datos. Toda unidad de trabajo debe preservar `cliente_id` como ancla de identidad del sistema.

La IA no capitanea: fabrica bajo contrato. Hermes no decide arquitectura ni despliega. Codex/Gemini no escriben fuera del scope. Nada toca core ni producción sin `cliente_id`, evidencia y gate humano.

## Flujo vigente con HITL obligatorio

```text
Owner Telegram / CLI
→ Hermes Gateway externo
→ propuesta de TaskSpec YAML
→ Gate Humano: APROBACIÓN DE SCOPE
→ Codex Builder externo en zona temporal
→ Gemini Auditor externo
→ ChatGPT Director/Auditor externo
→ Gate Humano: REVISIÓN DE EVIDENCIA
→ factory/hermes_control_cli.py como notario de evidencia
→ Zona de Handoff
→ Deploy manual / script firmado
```

## Roles

| Agente | Rol | Puede | No puede |
|---|---|---|---|
| Hermes Gateway | Orquestador conversacional externo | Leer gate, proponer TaskSpec, invocar adaptadores, registrar evidencia | Aprobar su propio scope, validar su propio trabajo, ejecutar runners legacy, desplegar |
| Codex | Builder externo | Modificar archivos permitidos por TaskSpec aprobada, ejecutar tests, emitir build report | Decidir arquitectura final, auditarse a sí mismo, tocar fuera de `allowed_files` |
| Gemini | Auditor técnico externo | Revisar diff, evidencia, tests y contratos | Ser Builder productivo por defecto, abrir gate humano |
| ChatGPT | Director/Auditor externo | Auditar evidencia, decidir próximo paso, redactar TaskSpecs | Ejecutar ciclos autónomos sin evidencia, desplegar |
| Owner | Gate humano | Aprobar scope, revisar evidencia, autorizar deploy | Delegar deploy automático sin revisión |

## Unidad de trabajo

La unidad de trabajo vigente es una TaskSpec YAML en:

```text
factory/ai_governance/tasks/*.yaml
```

La TaskSpec debe incluir `cliente_id`, `allowed_files`, `forbidden_files`, `required_tests`, `evidence_path` y `gate`. El modelo `factory/hallazgos/<state>/*.md` queda como antecedente histórico o dominio de negocio, no como cola activa de factoría.

## Veredictos canónicos de handoff

Los estados legacy quedan reemplazados por el vocabulario de `_BOVEDA_PURIFICADA/VALOR_ALTO_ESTRUCTURAL/factory/ai_governance/contracts/verdict_enum.yaml`.

| Veredicto | Significado operacional | Autoriza movimiento |
|---|---|---|
| `SUCCESS_CODE` | Código generado y validado sintácticamente. | NO |
| `SUCCESS_FACTORY` | Módulo estanco, con `cliente_id`, evidencia y listo para handoff. | Solo con Gate Humano |
| `VALIDATED_ARCH` | La propuesta respeta Editorial Monolith y Sacred Modernism. | Solo combinado con `SUCCESS_FACTORY` y Gate Humano |
| `BLOCKED_MISSING_ASSET` | Falta un archivo o contrato referenciado en el índice. | NO |
| `BLOCKED_AMBIGUOUS_SPEC` | La TaskSpec contiene instrucciones contradictorias o vagas. | NO |
| `BLOCKED_IDENTIDAD_CONFLICT` | Se detectó uso de `tenant_id` o falta `cliente_id`. | NO |
| `REJECTED_STACK` | La propuesta usa tecnologías fuera del stack permitido. | NO |
| `REJECTED_INFERENCE` | El agente propuso lógica basada en documentos conceptuales. | NO |
| `REJECTED_SECURITY` | El código vulnera aislamiento de datos entre clientes. | NO |
| `FAILED_LINT` | El código no pasa validación de PEP8 o tipos. | NO |
| `FAILED_RUNTIME` | Error en dry-run del módulo. | NO |

## Jerarquía de éxito

1. `SUCCESS_CODE`: el código corre o valida sintaxis. No autoriza movimiento de archivos ni handoff.
2. `VALIDATED_ARCH`: la arquitectura respeta los contratos del SME OS.
3. `SUCCESS_FACTORY`: el módulo es estanco, tiene `cliente_id`, evidencia y puede pasar a handoff.

Bloqueo maestro: ninguna pieza se mueve al repositorio real sin el combo `SUCCESS_FACTORY` + `VALIDATED_ARCH` firmado por el Auditor y validado por el Owner.

## Gate Humano Obligatorio

Hay dos gates humanos no salteables:

1. Gate de Scope: antes de construir, el Owner debe aprobar la TaskSpec, `allowed_files`, `forbidden_files`, `cliente_id`, tests y evidencia esperada.
2. Gate de Evidencia: después de auditoría, el Owner debe revisar evidencia, diff, tests y veredictos antes de cualquier handoff.

El deploy queda siempre bloqueado hasta ejecución manual o script firmado por el Owner.

## Protocolo NO TOCAR CORE

Cualquier TaskSpec que incluya rutas bajo `/app/core`, `/core`, `/kernel` o `/auth` activa `HUMAN_OVERRIDE_REQUIRED`.

Reglas:

- requiere `allowed_files` cerrado y explícito;
- requiere revisión línea por línea del Owner;
- prohíbe `rsync`, `cp`, movimientos masivos o globbing sobre rutas core;
- exige evidencia ampliada de diff, tests y justificación;
- si falta autorización humana, el veredicto debe ser `BLOCKED_AMBIGUOUS_SPEC` o `REJECTED_SECURITY` según el riesgo.

## Payload Hermes → Codex

Debe cumplir `_BOVEDA_PURIFICADA/VALOR_ALTO_ESTRUCTURAL/factory/ai_governance/schemas/agent_handoff.schema.json`.

Campos mínimos:

```json
{
  "task_id": "string",
  "repo_ref": "main|commit_sha|branch",
  "source_agent": "hermes_gateway",
  "target_agent": "codex_builder",
  "allowed_files": ["path"],
  "forbidden_files": ["path"],
  "required_tests": ["command"],
  "evidence_path": "factory/evidence/<task_id>",
  "context_files": ["path"],
  "cliente_id": "string",
  "human_scope_approved": false
}
```

## Payload Codex → Hermes/Gemini

Debe cumplir `_BOVEDA_PURIFICADA/VALOR_ALTO_ESTRUCTURAL/factory/ai_governance/schemas/task_result.schema.json`.

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

Debe cumplir `_BOVEDA_PURIFICADA/VALOR_ALTO_ESTRUCTURAL/factory/ai_governance/schemas/audit_result.schema.json`.

Incluye:

- `task_id`
- `agent_id`
- `verdict`
- `cliente_id`
- `gate_open`
- `violations`
- `evidence_reviewed`
- `required_fixes`
- `risk_level`

## Protocolo de Rechazo por Identidad

Cualquier entrega que no incluya el campo `cliente_id` o que haga referencia a `tenant_id` debe ser rechazada con el veredicto `BLOCKED_IDENTIDAD_CONFLICT`.

Esta regla aplica a TaskSpecs, payloads Hermes → Codex, payloads Codex → Gemini, payloads Gemini → ChatGPT, modelos Pydantic, tablas SQL, repositorios de persistencia y documentación contractual nueva.

No se acepta una entidad operativa huérfana en el SME OS.

## Rol de `factory/hermes_control_cli.py`

`factory/hermes_control_cli.py` actúa como notario de evidencia, no como instalador ni deployer.

Puede:

- registrar logs de evidencia;
- mover artefactos validados a zona de handoff;
- escribir hashes de archivos y referencias de commit;
- preparar comandos de despliegue para revisión humana.

No puede:

- ejecutar deploy automático;
- modificar core por decisión propia;
- saltar Gate Humano;
- resolver arquitectura;
- convertir `SUCCESS_CODE` en autorización de movimiento.

## Ownership de evidencia

| Evidencia | Responsable |
|---|---|
| TaskSpec original | Hermes Gateway / repo |
| Aprobación de scope | Owner |
| Build output | Codex |
| Tests y comandos | Codex |
| Audit report | Gemini |
| Dictamen final | ChatGPT / Owner |
| Gate final | Owner |
| Registro notarial | hermes_control_cli.py |

Toda evidencia debe vivir bajo:

```text
factory/evidence/<task_id>/
```

## Rollback y errores

- Si Codex toca archivos fuera de `allowed_files`, veredicto `FAILED_RUNTIME` o `REJECTED_SECURITY`.
- Si faltan tests requeridos, veredicto `BLOCKED_MISSING_ASSET`.
- Si Gemini no puede verificar evidencia, veredicto `BLOCKED_MISSING_ASSET`.
- Si ChatGPT no puede leer evidencia reproducible, veredicto `BLOCKED_MISSING_ASSET`.
- Si aparece runner legacy activo, veredicto `REJECTED_STACK`.
- Si aparece `tenant_id` o falta `cliente_id`, veredicto `BLOCKED_IDENTIDAD_CONFLICT`.
- Si una TaskSpec toca core sin `HUMAN_OVERRIDE_REQUIRED`, el ciclo queda bloqueado.

## Referencias

- `docs/factory/RUNTIME_VIGENTE.md`
- `docs/factory/FACTORY_CONTRATO_OPERATIVO.md`
- `_BOVEDA_PURIFICADA/VALOR_ALTO_ESTRUCTURAL/factory/ai_governance/contracts/verdict_enum.yaml`
- `_BOVEDA_PURIFICADA/VALOR_ALTO_ESTRUCTURAL/factory/ai_governance/schemas/agent_handoff.schema.json`
- `_BOVEDA_PURIFICADA/VALOR_ALTO_ESTRUCTURAL/factory/ai_governance/schemas/task_result.schema.json`
- `_BOVEDA_PURIFICADA/VALOR_ALTO_ESTRUCTURAL/factory/ai_governance/schemas/audit_result.schema.json`
- `_BOVEDA_PURIFICADA/VALOR_ALTO_ESTRUCTURAL/factory/ai_governance/schemas/taskspec.schema.json`

## Historial de Cambios

- 2026-04-28 — Creado por remediación P1/P2 para cerrar F-012 y F-029.
- 2026-04-29 — Purificado para SME OS: estados legacy reemplazados por veredictos canónicos e inyección obligatoria de soberanía `cliente_id`.
- 2026-04-29 — Elevado a v2.0 HITL: Gate Humano Obligatorio, NO TOCAR CORE, `SUCCESS_CODE` sin autorización de movimiento y CLI como notario de evidencia.
