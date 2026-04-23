# HALLAZGO

## META
- id:
- estado: pending
- modulo_objetivo:
- prioridad:
- origen: gemini-vertex
- repo_destino: E:\BuenosPasos\smartbridge\SmartPyme

## OBJETIVO

## RUTAS_FUENTE

## SLICES_CANDIDATOS

## TOP_SLICES

## PROPUESTA_DE_PORTADO
### Crear o modificar solo:

## REGLAS_DE_EJECUCION
- no tocar otros módulos salvo imports mínimos imprescindibles
- no refactor global
- no inventar rutas
- fail-closed obligatorio
- humano en el loop obligatorio
- si falta contexto, bloquear y preguntar
- correr tests mínimos del módulo

## CRITERIO_DE_CIERRE

## DUDAS_DETECTADAS

## PREGUNTA_AL_OWNER

## EJECUCION_CODEX
- estado_final:
- archivos_modificados:
- tests_ejecutados:
- resumen:

## BLOQUEO
- motivo:
- decision_requerida_del_owner:
- impacto_si_no_se_responde:

---

## EJEMPLO_MINIMO_REALISTA (SOLO EJEMPLO, NO EJECUTAR DIRECTO)

# HALLAZGO

## META
- id: HZ-2026-04-20-EX-CLAR-001
- estado: pending
- modulo_objetivo: clarification
- prioridad: alta
- origen: gemini-vertex
- repo_destino: E:\BuenosPasos\smartbridge\SmartPyme

## OBJETIVO
Portar al módulo de clarification de SmartPyme la lógica de trazabilidad de preguntas y persistencia de estado de revisión, manteniendo contratos locales y fail-closed.

## RUTAS_FUENTE
- E:\BuenosPasos\smartcounter\app\core\clarification\service.py
- E:\BuenosPasos\smartcounter\app\core\clarification\models.py
- E:\BuenosPasos\smartbridge\shared\clarification\state_machine.py

## SLICES_CANDIDATOS
- slice-A: modelo de dominio para solicitud/respuesta de clarification
- slice-B: servicio para crear, actualizar y resolver estados de clarification
- slice-C: persistencia de eventos y estado final de clarification
- slice-D: utilitario global de auditoría transversal (descartar por alcance)

## TOP_SLICES
- slice-A
- slice-B
- slice-C

## PROPUESTA_DE_PORTADO
### Crear o modificar solo:
- E:\BuenosPasos\smartbridge\SmartPyme\app\core\clarification\models.py
- E:\BuenosPasos\smartbridge\SmartPyme\app\core\clarification\service.py
- E:\BuenosPasos\smartbridge\SmartPyme\app\core\clarification\persistence.py
- E:\BuenosPasos\smartbridge\SmartPyme\tests\core\test_clarification_service.py

## REGLAS_DE_EJECUCION
- no tocar otros módulos salvo imports mínimos imprescindibles
- no refactor global
- no inventar rutas
- fail-closed obligatorio
- humano en el loop obligatorio
- si falta contexto, bloquear y preguntar
- correr tests mínimos del módulo

## CRITERIO_DE_CIERRE
- El flujo de clarification permite crear consulta, registrar respuesta y cerrar estado sin romper contratos locales.
- Tests mínimos del módulo `clarification` pasan en local.
- No hay cambios fuera de archivos autorizados.

## DUDAS_DETECTADAS
- No está definido si el estado `needs_owner_input` debe persistirse como estado terminal o transitorio antes de `blocked`.

## PREGUNTA_AL_OWNER
¿Confirmás si `needs_owner_input` en clarification debe persistirse como estado terminal en base de datos o solo como estado transitorio previo a `blocked`?

## EJECUCION_CODEX
- estado_final:
- archivos_modificados:
- tests_ejecutados:
- resumen:

## BLOQUEO
- motivo:
- decision_requerida_del_owner:
- impacto_si_no_se_responde:
