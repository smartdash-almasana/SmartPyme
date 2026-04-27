# HALLAZGO

## META
- id: HZ-2026-04-27-FACTORY-003
- estado: pending
- modulo_objetivo: hermes-orchestrator-loop
- prioridad: critica
- origen: architect
- repo_destino: SmartPyme

## OBJETIVO
Implementar el loop deterministico minimo que permita a Hermes operar SmartPyme Factory sobre hallazgos markdown con evidencia y estados persistentes.

Este hallazgo NO conecta todavia Vertex/Gemini real. Primero debe existir el kernel deterministico.

## CONTEXTO
Hermes Agent ya posee loop de agente, tools, subagentes y delegate_task. SmartPyme no debe fabricar otro Hermes. SmartPyme debe exponer un contrato deterministico para que Hermes pueda operar sobre el repo.

Unidad real de trabajo:

`factory/hallazgos/*.md`

Estados persistentes:

`pending -> in_progress -> done | blocked`

## RUTAS_OBJETIVO
Se permite crear o modificar solo:

- factory/orchestrator/__init__.py
- factory/orchestrator/hallazgo_store.py
- factory/orchestrator/evidence_store.py
- factory/orchestrator/agent_runner.py
- factory/orchestrator/hermes_loop.py
- tests/factory/test_hermes_loop.py

## RESTRICCIONES
- No tocar app/**
- No tocar core/**
- No tocar services/**
- No tocar SmartCounter Core
- No tocar integraciones externas
- No conectar Vertex todavia
- No usar APIs externas
- No ejecutar automatizacion continua
- No crear features de producto
- No modificar factory/run_factory.py
- No modificar factory/run_codex_worker.py
- No modificar factory/continuous_factory.py

## TAREAS_EJECUCION

### 1. Crear HallazgoStore
Implementar en `factory/orchestrator/hallazgo_store.py` funciones deterministicas:

- `list_pending()`
- `read_hallazgo(path)`
- `move_to_in_progress(path)`
- `move_to_done(path)`
- `move_to_blocked(path, reason)`

Reglas:

- usar `pathlib.Path`
- crear directorios si faltan
- no pisar archivos existentes
- si destino existe, usar sufijo incremental `-01`, `-02`
- devolver rutas finales

### 2. Crear EvidenceStore
Implementar en `factory/orchestrator/evidence_store.py`:

- `write_builder_report(hallazgo_id, content)`
- `write_auditor_report(hallazgo_id, content)`
- `write_status(hallazgo_id, data)`
- `write_text(hallazgo_id, filename, content)`

Destino:

`factory/evidence/<hallazgo_id>/`

### 3. Crear AgentRunner mock
Implementar en `factory/orchestrator/agent_runner.py`:

- clase `MockAgentRunner`
- `run_builder(hallazgo_text)` devuelve status `submitted`
- `run_auditor(hallazgo_text, builder_report)` devuelve verdict `VALIDADO`

Este mock solo sirve para testear el loop sin IA.

### 4. Crear HermesLoop deterministico
Implementar en `factory/orchestrator/hermes_loop.py`:

- `run_one_cycle(repo_root, agent_runner=None)`

Comportamiento:

1. buscar primer hallazgo pending
2. si no hay pending, devolver `{"status": "idle"}`
3. mover a in_progress
4. ejecutar builder mock
5. guardar evidencia builder
6. ejecutar auditor mock
7. guardar evidencia auditor
8. si VALIDADO mover a done
9. si NO_VALIDADO o error mover a blocked
10. devolver dict con status, hallazgo_id, final_state y evidence_dir

### 5. Tests
Crear `tests/factory/test_hermes_loop.py` con tests usando `tmp_path`:

- idle si no hay pending
- pending pasa a done cuando auditor valida
- se crea evidence/<hallazgo_id>/builder_report.md
- se crea evidence/<hallazgo_id>/auditor_report.md
- no quedan archivos en pending tras ciclo exitoso
- si auditor devuelve NO_VALIDADO, el hallazgo termina en blocked

## CRITERIOS_DE_ACEPTACION
- Existen todos los archivos de `RUTAS_OBJETIVO`
- `pytest tests/factory/test_hermes_loop.py -v` pasa
- No se modifica código fuera de `factory/orchestrator/**` y `tests/factory/test_hermes_loop.py`
- El loop funciona sin Vertex, sin Gemini y sin red
- La evidencia queda persistida en `factory/evidence/<hallazgo_id>/`
- `run_one_cycle` devuelve estructura parseable como dict

## VALIDACIONES

```bash
python -m pytest tests/factory/test_hermes_loop.py -v
git diff --name-only
```

## SALIDA_BUILDER
Debe reportar:

- archivos creados
- resumen de implementación
- salida de pytest
- diff name-only
- riesgos o bloqueos

## SALIDA_AUDITOR
Debe validar:

- alcance respetado
- tests pasan
- no se tocó producto
- evidencia existe
- veredicto VALIDADO o NO_VALIDADO

## DUDAS_DETECTADAS
- ninguna

## PREGUNTA_AL_OWNER
- null
