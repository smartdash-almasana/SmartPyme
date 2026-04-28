# HERMES PROFESSIONAL RESET PLAN — SmartPyme Factory

Estado: CANONICO v1

## Decision

Se declara obsoleta la gobernanza basada en parches sobre scripts aislados.

El sistema actual sirve como evidencia historica, pero no como arquitectura final de la factoria.

## Problema

La factoria actual mezcla responsabilidades:

- Telegram controla estado operativo con scripts caseros.
- Hermes real no esta expresado como capa profesional completa.
- Codex ejecuta, pero la decision de ciclo no esta suficientemente gobernada.
- Gemini esta mencionado, pero no integrado como auditor runtime verificable.
- REPO_CLEAN existe como contrato, pero no como politica transversal plenamente aplicada.
- Los botones Telegram no son un protocolo robusto de gates.

## Principio de reset

No se borra evidencia ni historia.

Se depreca lo viejo, se aisla lo parcheado y se construye una gobernanza profesional por capas.

## Arquitectura objetivo

```text
Owner Telegram
  -> Hermes Gateway
  -> SmartPyme Factory Skill
  -> REPO_CLEAN Guard
  -> Environment Guard
  -> Task Queue Controller
  -> Codex Builder
  -> Gemini Auditor
  -> Evidence Gate
  -> Human Audit Gate
```

## Capas obligatorias

### 1. REPO_CLEAN Guard

Debe correr antes y despues de cada ciclo. Si falla, no hay dispatch.

### 2. Environment Guard

Valida Python, pytest, Ruff, Polars y contrato de entorno. Si falta algo, bloquea con causa exacta.

### 3. Telegram Gate

Los botones son idempotentes. Ningun boton puede crear loops.

### 4. Hermes Skill Layer

Las acciones recurrentes se modelan como skills/procedimientos, no como parches sueltos.

### 5. MCP Layer

Las operaciones sobre SmartPyme deben exponerse por tools verificables cuando correspondan.

### 6. Builder Layer

Codex solo construye bajo task spec acotada.

### 7. Auditor Layer

Gemini debe integrarse como auditor verificable o declararse no integrado.

## Estado de componentes actuales

```text
scripts/hermes_factory_runner.py         LEGACY_ORCHESTRATOR
scripts/telegram_factory_control.py      LEGACY_TELEGRAM_CONTROL
scripts/telegram_trigger_cycle.py        LEGACY_TRIGGER
factory/telegram_notify.py               LEGACY_NOTIFY
factory/ai_governance/tasks/*.yaml       ACTIVE_QUEUE_LEGACY
factory/evidence/**                      EVIDENCE_KEEP
```

## Politica

No se elimina nada sin task explicita. Lo viejo se marca legacy y se reemplaza por capas nuevas verificables.

## Orden de implementacion

1. Congelar cola de producto.
2. Implementar REPO_CLEAN como guard transversal real.
3. Implementar Environment Guard.
4. Hacer Telegram idempotente y seguro.
5. Definir skill SmartPyme Factory.
6. Definir skill Repo Clean.
7. Definir skill Environment Setup.
8. Integrar Gemini Auditor como paso verificable.
9. Recien despues reactivar tareas de producto.

## Regla final

No mas parches sin diseño. Toda nueva unidad debe tener task spec, evidencia y criterio de cierre.
