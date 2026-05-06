# BLUEPRINT_001_FACTORIA_LOW_COST_MULTIAGENTE

## VEREDICTO

SmartPyme Factory debe reiniciarse desde un blueprint nuevo, low-cost y por capas.

No se debe seguir creciendo `queue_runner.py` ni reintentar HITO_010, HITO_011 o HITO_012 sobre la arquitectura anterior.

El baseline técnico sano es:

```text
HITO_009
commit: 86237e4
rama: factory/ts-006-jobs-sovereign-persistence
```

Ese baseline conserva lo útil:

- Docker sandbox real.
- Validación de comandos peligrosos.
- ApprovalGate local.
- Estado `WAITING_FOR_APPROVAL`.
- Patrón fail-closed.
- Tests base de Docker/Approval.

A partir de ahí, el desarrollo debe continuar con una factoría nueva, modular, barata de operar y basada en agentes intercambiables.

---

## OBJETIVO DEL NUEVO BLUEPRINT

Construir una factoría multiagente para generar código de SmartPyme con bajo costo operativo.

La factoría debe producir:

- Código Python backend.
- FastAPI.
- Contratos Pydantic.
- Tests pytest.
- Adaptadores.
- Scripts operativos seguros.
- PRs en GitHub.
- Evidencia mínima por tarea.

La factoría no debe depender de modelos pagos para funcionar.

Los modelos pagos deben ser refuerzos puntuales, no el centro del sistema.

---

## PRINCIPIOS

1. Agentes pequeños.
2. Responsabilidades separadas.
3. Contratos Pydantic entre capas.
4. Ejecución solo en Docker.
5. GitHub como fuente de verdad.
6. Humano aprueba decisiones críticas.
7. Modelos locales o gratuitos primero.
8. Modelos pagos solo por escalamiento.
9. No monolitos cognitivos.
10. No prompts gigantes como mecanismo operativo permanente.

---

## STACK PRINCIPAL LOW-COST

```text
LangGraph     = orquestación multiagente/stateful
Ollama        = modelos locales baratos
Pydantic      = contratos
Docker        = sandbox
GitHub        = ramas, diff, PR
Hermes        = humano/HITL/Telegram
Prefect       = jobs durables en fase posterior
Gemini        = auditoría/refuerzo puntual
DeepSeek Pro  = implementación difícil/refuerzo puntual
Codex         = agente externo opcional
```

---

## ROL DE CADA HERRAMIENTA

### LangGraph

Debe ser el orquestador principal del flujo multiagente.

Hace:

- Coordinar nodos.
- Mantener estado.
- Manejar ciclos controlados.
- Cortar loops.
- Pausar para aprobación humana.
- Reanudar trabajos.

No hace:

- No ejecuta comandos directamente en host.
- No guarda secretos.
- No reemplaza GitHub.
- No decide merge final.

---

### Ollama / modelos locales

Debe ser la base barata de inferencia.

Hace:

- Clasificaciones simples.
- Resúmenes cortos.
- Revisión básica.
- Generación inicial de código simple.
- Tareas de bajo riesgo.

Modelos candidatos:

- Qwen coder.
- DeepSeek coder local si está disponible.
- CodeGemma.
- Llama coder variants.
- Nemotron local si aplica.

No hace:

- No toma decisiones finales de arquitectura.
- No aprueba PR.
- No toca GitHub directo.

---

### Pydantic

Gobierna contratos.

Contratos mínimos:

- `TaskSpec`
- `AgentTask`
- `PatchPlan`
- `ExecutionRequest`
- `ExecutionResult`
- `ReviewResult`
- `ApprovalRequest`
- `ApprovalDecision`
- `EvidenceBundle`
- `CommitPlan`

No orquesta ni ejecuta.

---

### Docker

Única capa autorizada para ejecutar código generado.

Hace:

- Ejecutar tests.
- Ejecutar linters.
- Capturar stdout/stderr/exit_code.
- Aplicar timeout.
- Bloquear red por defecto.

No hace:

- No monta credenciales.
- No monta home.
- No usa Docker socket.
- No corre privilegiado.

---

### GitHub

Fuente de verdad.

Hace:

- Branch por tarea.
- Diff.
- PR.
- Review.
- Historial.

No hace:

- No merge automático en fase inicial.
- No deploy automático.

---

### Hermes

Gateway humano.

Hace:

- Recibir intención.
- Mostrar evidencia.
- Pedir aprobación.
- Rechazar o reintentar.
- Reportar `MODEL_REAL` cuando use modelos externos.

No hace:

- No ejecuta código.
- No orquesta todo.
- No reemplaza LangGraph.
- No debe pedir al humano operar la terminal todo el tiempo.

---

### Prefect

Fase posterior.

Hace:

- Jobs largos.
- Retries.
- Scheduling.
- Watchdog.
- Observabilidad operacional.

No entra en la primera POC si agrega fricción.

---

### Gemini / DeepSeek Pro / Codex

Modelos de refuerzo.

Uso recomendado:

- Gemini: diseño, auditoría amplia, revisión conceptual.
- DeepSeek Pro: implementación difícil, refactors técnicos, diagnóstico de tests.
- Codex: agente de coding externo opcional con rama aislada.

Regla:

```text
Si MODEL_REAL no coincide con MODEL_TARGET, la salida no se usa para WRITE.
```

---

## ARQUITECTURA POR CAPAS

```text
Owner / Humano
  ↓
Hermes
  ↓
IntentRequest / ApprovalRequest
  ↓
LangGraph FactoryGraph
  ↓
Pydantic Contracts
  ↓
Agentes low-cost/locales
  ↓
PatchPlan
  ↓
Docker Sandbox
  ↓
ExecutionResult
  ↓
ReviewerAgent
  ↓
EvidenceBundle
  ↓
CommitPlan
  ↓
GitHub Branch / PR
  ↓
Hermes Approval
  ↓
Merge humano/controlado
```

---

## GRAFO MÍNIMO

Primera versión de LangGraph:

```text
receive_task
  → audit_scope
  → plan_patch
  → generate_patch
  → run_sandbox
  → review_result
  → prepare_pr
  → wait_human_approval
```

Nodos:

1. `AuditNode`
2. `PlannerNode`
3. `ImplementerNode`
4. `SandboxNode`
5. `ReviewerNode`
6. `GitHubPlanNode`
7. `ApprovalNode`

---

## MODELO DE COSTOS

Prioridad:

```text
Nivel 0: lógica determinística Python
Nivel 1: modelo local Ollama
Nivel 2: modelo free/rate-limited
Nivel 3: Gemini/DeepSeek pago para casos difíciles
Nivel 4: humano decide
```

Regla:

```text
No usar modelo pago para tareas que puede resolver un script determinístico o modelo local.
```

---

## QUÉ CONSERVAR DEL REPO ACTUAL

Desde HITO_009:

- DockerExecutor.
- Command policy.
- ApprovalGate local.
- TaskSpec base si está limpio.
- Tests Docker/Approval.
- Patrón fail-closed.

---

## QUÉ NO SEGUIR

No continuar:

- HITO_010 anterior.
- HITO_011 anterior.
- HITO_012 anterior.
- Crecimiento de `queue_runner.py`.
- Runners que mezclan aprobación, ejecución, evidencia, git y modelos.

---

## POC MÍNIMA

Objetivo de la POC:

Demostrar una tarea chica de generación de código usando LangGraph + modelo local + Docker + GitHub.

Tarea ejemplo:

```text
Crear función Python simple + test pytest.
```

Flujo:

1. Crear `TaskSpec` manual.
2. LangGraph ejecuta `AuditNode`.
3. `ImplementerNode` usa modelo local.
4. Se genera patch en rama temporal.
5. Docker ejecuta pytest.
6. `ReviewerNode` emite veredicto.
7. Se prepara PR o PR simulado.
8. Hermes o humano aprueba.

Criterio PASS:

- No ejecución en host.
- Test pasa en Docker.
- Evidencia existe.
- Diff está limitado.
- No merge automático.
- Modelo usado queda registrado.

---

## ROADMAP

### Fase 0 — Freeze

- Baseline HITO_009.
- Documentar arquitectura nueva.
- No seguir queue_runner.

### Fase 1 — Contratos mínimos

- `TaskSpec`
- `GraphRunState`
- `ExecutionResult`
- `EvidenceBundle`
- `ReviewResult`

### Fase 2 — LangGraph POC

- Grafo mínimo.
- Nodos fake/determinísticos primero.
- Luego modelo local.

### Fase 3 — Docker integrado

- Sandbox real.
- Tests.
- Captura logs.

### Fase 4 — GitHub PR plan

- Branch.
- Diff.
- PR draft o simulado.

### Fase 5 — Hermes HITL

- Aprobación humana.
- Rechazo.
- Reintento.

### Fase 6 — Model routing

- Ollama default.
- Gemini/DeepSeek como escalamiento.
- `MODEL_REAL` obligatorio.

### Fase 7 — Prefect

- Jobs durables.
- Retries.
- Scheduling.

---

## DECISIÓN FINAL

SmartPyme Factory debe ser una factoría multiagente low-cost, no una cadena de prompts manuales ni un runner monolítico.

La primera POC debe ser chica, barata y verificable.

El principio rector:

```text
Agentes intercambiables, contratos estrictos, Docker obligatorio, GitHub visible, humano aprueba.
```
