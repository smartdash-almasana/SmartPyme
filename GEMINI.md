# SmartPyme / SmartTimes

## Fuente de verdad
Leé primero y respetá siempre estos archivos:

- docs/architecture/smarttimes_full_architecture.md
- docs/architecture/smartcounter_informe_analitico.docx
- docs/architecture/smartcounter_consistency_validation_framework.pdf
- docs/architecture/smartcounter_orchestration_state_machine.pdf

## Reglas absolutas
- No mover lógica fiscal, contable o monetaria crítica al LLM.
- El core de negocio debe ser determinístico en Python.
- Toda ambigüedad debe bloquear en AWAITING_VALIDATION.
- No usar float en rutas fiscales o monetarias críticas.
- No generar hallazgos sin entidad, diferencia, comparación y fuente.
- El Auditor tiene veto absoluto.
- El Constructor nunca despliega.
- No hacer UI, dashboards ni marketing mientras no esté cerrada la base del core y de la factoría.
- No inventar arquitectura fuera de los documentos fuente.
- Toda transición de estado debe ser trazable.

## Objetivo actual
Construir la base de la factoría industrial y del core completo:

1. state machine de fabricación
2. contratos explícitos
3. nodos por rol
4. persistencia de clarifications
5. findings accionables
6. tests de transición y regresión

## Forma de trabajo
- Un objetivo por iteración.
- Cambios mínimos, auditables y trazables.
- Antes de editar, leer la arquitectura fuente.
- Antes de escribir, mostrar plan corto.
- Responder en castellano.
- No crear archivos innecesarios.
- No tocar cloud, MCP, bots o despliegue salvo instrucción explícita.

## Entregables esperados
Cuando implementes cambios, devolvé siempre:

1. veredicto
2. archivos creados o editados
3. diff o resumen de cambios
4. riesgos detectados
5. siguiente átomo recomendado