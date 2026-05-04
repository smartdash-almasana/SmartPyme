# Capa 03 – Ciclo técnico cerrado

**Fecha de cierre:** 2026-05-04 21:32:35
**Rama:** factory/ts‑006‑jobs‑sovereign‑persistence
**Commit:** $(git rev-parse HEAD)

## Capa cerrada
Capa 03 (OperationalCase → DiagnosticReport → ActionProposal) ha completado su ciclo técnico de integración mínima.

## Contratos creados
- `OperationalCase` – contrato Pydantic que define un caso operativo con campos: `cliente_id`, `case_id`, `job_id`, `skill_id`, `hypothesis`, `evidence_ids`, `status`.
- `DiagnosticReport` – contrato Pydantic para informes de diagnóstico (existe, no integrado aún).
- `ActionProposal` – contrato Pydantic para propuestas de acción (existe, no integrado aún).

## Integración realizada
1. `OperationalCaseRepository.create_case` ahora acepta `OperationalCase` de Capa 03 y lo convierte internamente al contrato legado (`OperationalCaseContract`) para persistencia, manteniendo compatibilidad.
2. `OperationalCaseOrchestrator` está integrado con el contrato `OperationalCase` de Capa 03 (commit `0db2184`). Ya no utiliza el contrato legado `operational_case_contract`.
3. Corrección mínima: el orquestador no crea casos sin evidencia mínima (commit `fe91cce`). Si faltan `variables` y `evidence`, devuelve `CLARIFICATION_REQUIRED`.

## Tests
- `tests/contracts/test_layer_03_contracts.py` – 11 tests PASSED (100%).
- Incluye test de integración `test_capa03_operational_case_integration_with_repository`.
- `tests/ai/test_operational_case_orchestrator.py` – 9 tests PASSED (100%) con validaciones actualizadas.

## Límites
1. **No hay diagnóstico técnico todavía** – Los contratos están definidos, pero no hay flujo de diagnóstico implementado.
2. **No hay DiagnosticReport integrado todavía** – El contrato existe, pero no se usa en ningún pipeline.
3. **No hay ActionProposal integrado todavía** – El contrato existe, pero no se genera ni valida.
4. **No hay MCP** – No se ha expuesto ninguna herramienta MCP para Capa 03.

## Riesgos pendientes
1. **Compatibilidad entre contrato nuevo y legacy** – La heurística de validación de `hypothesis` difiere: el contrato legacy exige verbo investigativo o `?`; el contrato Capa 03 solo valida no vacío. Puede causar `ValueError` en conversión.
2. **DiagnosticReport pendiente** – La siguiente integración requiere conectar `DiagnosticReport` al flujo de diagnóstico.

## Próxima fase
**Capa 03 / FASE INTEGRAR** – Conectar `DiagnosticReport` al flujo de diagnóstico, manteniendo compatibilidad con el contrato `OperationalCase` ya integrado.

---

*Este documento cumple con la fase DOCUMENTAR del protocolo operativo de SmartPyme Factory (ver `docs/factory/AGENT_WORKFLOW.md`).*