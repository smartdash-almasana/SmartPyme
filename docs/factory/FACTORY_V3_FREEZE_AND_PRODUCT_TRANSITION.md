# Factory V3 — Freeze de Infraestructura y Transición a Producto

## Estado

**VEREDICTO:** PASS FINAL  
**RAMA BASE:** `main`  
**HITO:** Runtime Sandbox Worker  
**READY_TO_FREEZE_INFRA:** YES

Este documento formaliza el cierre del hito mínimo operativo de Factory V3 y fija la transición estratégica hacia Producto / Laboratorio PyME.

Factory V3 ya alcanzó el umbral suficiente de infraestructura viva: puede tomar una tarea pendiente, ejecutarla en sandbox Docker real, producir artifact, marcar la tarea como terminada y reconstruir contexto mediante replay.

---

## Flujo validado

```text
Task PENDING
→ RuntimeSandboxWorker
→ SandboxBridge
→ DockerExecutor
→ Artifact
→ Task DONE
→ ContextRehydrator
→ RuntimeSnapshot
```

Este flujo fue validado en `main` con:

```text
PYTHONPATH=experiments/prefect-factory:. pytest tests/factory_v3 -q
```

Resultado reportado:

```text
7 passed
```

Los warnings observados provienen de deprecations internas de la librería Docker y no afectan el funcionamiento validado.

---

## Componentes cerrados

### Core soberano

```text
factory_v3/contracts
factory_v3/ledgers
factory_v3/runtime
factory_v3/prompting
```

Capacidades existentes:

```text
- AgentCard
- TaskEnvelope
- ArtifactEnvelope
- TaskEvent
- ArtifactLedger
- TaskLedger
- ContextRehydrator
- RuntimeSnapshot
- RuntimeLoop base
- RuntimeObservability
- Prompt governance
```

### Sandbox real

```text
factory_v3/runtime/sandbox_bridge.py
experiments/prefect-factory/factory_prefect/sandbox/docker_executor.py
experiments/prefect-factory/factory_prefect/contracts/sandbox.py
```

Capacidades validadas:

```text
- ejecución Docker efímera;
- network_disabled;
- timeout control;
- bloqueo de comandos peligrosos;
- requires_human_approval;
- reasons auditables;
- DOCKER_UNAVAILABLE controlado.
```

### Worker mínimo

```text
factory_v3/runtime/runtime_sandbox_worker.py
```

Responsabilidad validada:

```text
- leer tarea PENDING;
- ejecutar comando mediante SandboxBridge;
- registrar stdout como artifact TEST_REPORT;
- transicionar tarea a DONE;
- permitir rehidratación posterior.
```

---

## Tests relevantes

```text
experiments/prefect-factory/tests/test_docker_executor.py
tests/factory_v3/test_runtime_sandbox_e2e.py
tests/factory_v3/test_runtime_loop_sandbox_worker.py
tests/factory_v3/*
```

Estado consolidado:

```text
DockerExecutor: PASS
Sandbox E2E: PASS
RuntimeSandboxWorker: PASS
Factory V3 suite: PASS
```

---

## Qué demuestra este hito

Factory V3 ya puede:

```text
1. recibir una tarea pendiente;
2. consumirla con un worker mínimo;
3. ejecutar trabajo real aislado en Docker;
4. bloquear comandos peligrosos;
5. producir evidencia durable;
6. registrar artifact;
7. transicionar estado a DONE;
8. reconstruir contexto desde ledgers.
```

Esto convierte a Factory V3 en infraestructura operativa mínima viable.

---

## Qué NO se va a expandir ahora

Queda explícitamente fuera de alcance inmediato:

```text
- daemon runtime persistente;
- scheduler avanzado;
- worker pool distribuido;
- concurrencia industrial;
- Google ADK completo;
- A2A network real;
- integración Prefect real;
- UI de supervisión;
- orquestación multiagente compleja;
- runtime policies avanzadas;
- cluster orchestration.
```

Estos frentes no están descartados, pero quedan congelados hasta que Producto / Laboratorio PyME genere evidencia concreta que justifique su reapertura.

---

## Riesgo que se evita

El riesgo principal a partir de este punto es:

```text
sobreingeniería autoreferencial
```

Es decir:

```text
seguir construyendo runtime, A2A, scheduler y agentes distribuidos
sin validar valor operativo real en casos PyME.
```

Este freeze existe para impedir que la factoría se convierta en un fin en sí mismo.

---

## Decisión estratégica

A partir de este hito, la asignación recomendada es:

```text
70% Producto / Laboratorio PyME
30% Factoría estabilización
```

La factoría pasa a:

```text
modo infraestructura estable
```

El producto pasa a:

```text
modo aceleración
```

---

## Próximo foco: Producto / Laboratorio PyME

El frente prioritario pasa a ser construir valor operativo usable:

```text
- anamnesis operacional;
- ingesta de evidencia;
- curación de datos;
- OperationalCase;
- hipótesis investigable;
- investigación técnica;
- DiagnosticReport;
- hallazgos con entidad específica;
- diferencia cuantificada;
- comparación explícita de fuentes;
- SmartGraph contextual;
- asertividades operativas;
- reportes vendibles para PyME real.
```

La regla de producto se mantiene:

```text
SmartPyme no decide. SmartPyme propone. El dueño confirma.
```

---

## Criterio para reabrir factoría

Solo se debe reabrir expansión fuerte de factoría si aparece una necesidad concreta desde Producto, por ejemplo:

```text
- un caso real requiere concurrencia;
- un flujo PyME requiere scheduling persistente;
- un agente necesita ADK real;
- un cliente exige trazabilidad distribuida;
- un volumen de tareas justifica worker pool;
- un flujo operativo exige A2A real.
```

Sin evidencia de producto, no se expande infraestructura.

---

## Estado final

```text
Factory_V3 = infraestructura mínima viva
READY_TO_FREEZE_INFRA = YES
NEXT_FOCUS = Producto / Laboratorio PyME
```

---

## Frase rectora

```text
Factory V3 ya está suficientemente viva para dejar de ser el cuello de botella principal.
El próximo cuello es producto operacional usable.
```
