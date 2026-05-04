# Capa 03 – Ciclo técnico cerrado

**Fecha de cierre:** 2026-05-04 21:32:35  
**Rama:** factory/ts-006-jobs-sovereign-persistence  
**Estado:** cierre técnico incremental actualizado

## Capa cerrada

Capa 03 cubre el tramo:

```text
OperationalCase -> DiagnosticReport -> ActionProposal
```

El ciclo técnico actual deja cerrados:

1. contratos mínimos de Capa 03;
2. integración de `OperationalCase` en repositorio;
3. integración de `OperationalCase` en orquestador;
4. pieza interna mínima `DiagnosticService` para generar `DiagnosticReport` desde `OperationalCase`.

## Contratos creados

- `OperationalCase` — contrato de caso operativo con `cliente_id`, `case_id`, `job_id`, `skill_id`, `hypothesis`, `evidence_ids`, `status`.
- `DiagnosticReport` — contrato de resultado investigativo con `cliente_id`, `report_id`, `case_id`, `hypothesis`, `diagnosis_status`, `findings`, `evidence_used`, `reasoning_summary`.
- `ActionProposal` — contrato de propuesta posterior al diagnóstico; no representa decisión ni autorización.

## Integración realizada

1. `OperationalCaseRepository.create_case` acepta `OperationalCase` de Capa 03 y lo adapta internamente al contrato legacy para persistencia.
2. `OperationalCaseOrchestrator` está integrado con `OperationalCase` de Capa 03.
   - Commit: `0db2184`
3. Corrección mínima: `OperationalCaseOrchestrator` no crea casos sin variables/evidencia real mínima.
   - Si faltan `variables` y `evidence`, devuelve `CLARIFICATION_REQUIRED`.
   - Commit: `fe91cce`
4. `DiagnosticService` fue creado como pieza interna mínima.
   - Genera `DiagnosticReport` desde `OperationalCase`.
   - Preserva `cliente_id`, `case_id` e `hypothesis`.
   - `CONFIRMED` requiere `evidence_used` y `findings` no vacíos.
   - `INSUFFICIENT_EVIDENCE` permite `evidence_used` y `findings` vacíos.
   - No ejecuta acciones.
   - No autoriza nada.
   - No integra todavía al flujo operativo.
   - Commit: `7d2597e`

## Tests

- `tests/contracts/test_layer_03_contracts.py` — 11 tests PASSED.
- `tests/ai/test_operational_case_orchestrator.py` — 9 tests PASSED.
- `tests/services/test_diagnostic_service.py` — 7 tests PASSED.

## Límites actuales

1. `DiagnosticService` existe, pero todavía no está conectado al flujo operativo.
2. No existe persistencia específica de `DiagnosticReport`.
3. `ActionProposal` existe como contrato, pero no está integrado.
4. No hay MCP expuesto para Capa 03.
5. No hay ejecución de acciones ni autorización automática.

## Riesgos pendientes

1. `DiagnosticService` genera `report_id` con `uuid`; es aceptable para pieza interna mínima, pero al agregar persistencia puede convenir un generador inyectable o determinístico.
2. La integración futura de `DiagnosticReport` debe preservar la regla: sin evidencia trazable y hallazgos no hay `CONFIRMED`.
3. Cualquier futura integración con MCP debe pasar por contrato explícito, tests y autorización.

## Próxima fase recomendada

```text
CAPA: 03
FASE: INTEGRAR
MODEL_TARGET: CODEX
```

Objetivo recomendado:

```text
Conectar DiagnosticService al flujo existente de Capa 03 sin exponer MCP, sin crear ActionProposal y sin ejecutar acciones.
```

## Regla de cierre

Este documento cumple la fase DOCUMENTAR del workflow operativo definido en:

```text
docs/factory/AGENT_WORKFLOW.md
```
