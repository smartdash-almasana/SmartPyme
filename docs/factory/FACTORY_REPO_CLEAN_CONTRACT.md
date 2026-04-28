# FACTORY REPO CLEAN CONTRACT — SmartPyme Factory

Estado: CANONICO v1

## Regla maestra

La factoria SmartPyme no puede construir, auditar, instalar dependencias ni ejecutar tareas si el repo local no esta limpio.

Ley operativa:

```text
Arranca limpio. Trabaja con evidencia. Cierra limpio.
```

## Prioridad

Este contrato esta por encima de cualquier tarea de producto, arquitectura, dependencia, documentacion o automatizacion.

Orden obligatorio:

1. Repo limpio.
2. Pull seguro.
3. Gate.
4. Tarea.
5. Ejecucion Hermes/Codex.
6. Evidencia.
7. Commit/push si corresponde.
8. Repo limpio otra vez.

## Preflight obligatorio

Antes de cualquier ciclo, Hermes debe verificar:

```bash
git status --short
```

Condicion de avance:

```text
salida vacia = puede continuar
salida no vacia = BLOCKED_REPO_DIRTY
```

No se permite continuar si aparecen estados:

```text
DU
UU
DD
AA
AU
UA
```

Tampoco se permite continuar si hay archivos runtime trackeados, staged o unstaged.

## Archivos runtime prohibidos en tracking

Estos archivos son estado generado de VM. No son producto y no deben quedar versionados:

```text
factory/control/AUDIT_GATE.md
factory/control/FACTORY_STATUS.md
factory/control/PRIORITY_BOARD.md
factory/control/.telegram_cycle_lock
factory/control/.telegram_control_offset
factory/runner_logs/*
factory/logs/*
.env
.env.*
```

## Politica de bloqueo

Si el repo no esta limpio:

```text
estado = BLOCKED_REPO_DIRTY
```

Acciones obligatorias:

- no ejecutar tarea de producto;
- no llamar a Codex;
- no avanzar roadmap;
- no instalar dependencias;
- no aprobar ciclo;
- notificar causa exacta por Telegram.

## Reparacion permitida

Hermes puede reparar automaticamente solo basura runtime conocida:

- sacar del indice archivos runtime prohibidos;
- conservarlos localmente si son necesarios para ejecucion;
- confirmar que `.gitignore` los cubre;
- dejar evidencia del antes y despues.

Hermes no puede descartar cambios de codigo, documentacion o specs sin autorizacion humana.

## Cierre obligatorio

Despues de cada ciclo:

```bash
git status --short
```

Condicion de cierre:

```text
salida vacia = ciclo cerrable
salida no vacia = BLOCKED_REPO_DIRTY_AT_CLOSE
```

Si hay cambios validos de producto:

1. commit;
2. push;
3. verificar repo limpio.

Si hay cambios runtime:

1. no commitear;
2. asegurar ignore;
3. limpiar indice si fueron trackeados;
4. verificar repo limpio.

## Evidencia minima

Toda reparacion o bloqueo de limpieza debe dejar evidencia:

```text
factory/evidence/<task_id>/repo_status_before.txt
factory/evidence/<task_id>/repo_status_after.txt
factory/evidence/<task_id>/repo_clean_decision.txt
```

## Veredictos validos

```text
REPO_CLEAN
BLOCKED_REPO_DIRTY
BLOCKED_REPO_CONFLICT
BLOCKED_REPO_RUNTIME_TRACKED
BLOCKED_REPO_DIRTY_AT_CLOSE
```

## Regla final

Sin repo limpio, no hay factoria.
