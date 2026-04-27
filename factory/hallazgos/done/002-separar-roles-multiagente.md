# HALLAZGO

## META
- id: HZ-2026-04-27-FACTORY-002
- estado: pending
- modulo_objetivo: factory-roles
- prioridad: alta
- origen: architect
- repo_destino: SmartPyme

## OBJETIVO
Formalizar la separación estricta de roles operativos de la factoría multiagente: Architect, Builder y Auditor.

## TAREAS_EJECUCION
Crear o ajustar el archivo:

`docs/multiagente_roles_operativos.md`

El documento debe establecer:

- Architect solo diseña hallazgos.
- Builder solo ejecuta cambios permitidos por el hallazgo.
- Auditor solo valida evidencia.
- Ningún agente valida su propio trabajo.
- Todo cambio requiere Write → Verify → Report.
- Si no hay evidencia verificable, estado = NO VALIDADO.

## RUTAS_OBJETIVO
- docs/multiagente_roles_operativos.md

## REGLAS_DE_EJECUCION
- No tocar código Python.
- No tocar tests.
- No tocar app/core/services.
- No ejecutar worker.
- No ejecutar factoría.
- No hacer commit desde Builder.

## CRITERIO_DE_CIERRE
- Existe `docs/multiagente_roles_operativos.md`.
- El documento menciona Architect, Builder y Auditor.
- El documento contiene la regla: `Ningún agente valida su propio trabajo`.
- El documento contiene `Write → Verify → Report`.
- El documento contiene `NO VALIDADO`.
- No se modifica código Python.
- No se modifican tests.

## COMANDOS_DE_VALIDACION_PROPUESTOS
```bash
test -f docs/multiagente_roles_operativos.md
grep -n "Ningún agente valida su propio trabajo" docs/multiagente_roles_operativos.md
grep -n "Write → Verify → Report" docs/multiagente_roles_operativos.md
grep -n "NO VALIDADO" docs/multiagente_roles_operativos.md
git status --short
```

## DUDAS_DETECTADAS
- ninguna

## PREGUNTA_AL_OWNER
- null
