# SmartPyme Blueprint Alignment — Factory Contracts

## Estado

HITO 06 — Alineación entre la factoría soberana y el Blueprint Técnico SmartPyme v1.0.

Este documento conecta la arquitectura de producto SmartPyme con los contratos operativos de SmartPyme Factory.

Regla central:

```text
La factoría no reemplaza al producto.
La factoría construye el producto con el mismo principio arquitectónico:
entrada tipada → procesamiento controlado → evidencia → decisión → salida auditada.
```

---

## 1. Correspondencia principal

| Blueprint SmartPyme | Factory SmartPyme | Equivalencia operativa |
|---|---|---|
| AI Layer interpreta | MODEL_TARGET / proveedor ejecutor | El modelo interpreta o ejecuta una tarea acotada |
| Pydantic valida | TaskSpec JSON / IO contracts | Toda entrada debe cumplir contrato antes de ejecutarse |
| Hard Core decide | TaskLoop soberano | El runner aplica reglas determinísticas de estado, gate y evidencia |
| Owner confirma | GPT_COPILOTO_CHAT + usuario | La decisión humana gobierna hitos, bloqueos y cambios de frente |
| Evidencia trazable | factory/evidence/<task_id>/ | Cada ciclo deja archivos reproducibles y JSON auditables |
| Jobs controlados | TaskSpec pending/in_progress/done/blocked | Cada tarea tiene ciclo de vida explícito |
| Persistencia soberana | GitHub + TaskSpecStore + evidencia versionada | La realidad compartida queda en repo, no en chat |

---

## 2. Invariante común

El Blueprint define:

```text
LLM interpreta.
Pydantic valida.
Core decide.
Dueño confirma.
```

La factoría aplica el mismo patrón:

```text
Agente/modelo interpreta la TaskSpec.
TaskSpec JSON valida el alcance.
TaskLoop decide estado y evidencia.
GPT/Usuario confirma el siguiente hito.
```

Esto evita que Hermes, Gemini, DeepSeek, Codex, Kiro o GPT actúen como autoridad final fuera de protocolo.

---

## 3. Contratos JSON derivados

Los contratos del TaskLoop se alinean con los contratos futuros del producto:

| Contrato Factory | Futuro contrato Producto | Propósito común |
|---|---|---|
| TaskSpec JSON | IngestPayload / OwnerDemand | Entrada estructurada de trabajo |
| ExecutionResult JSON | JobExecutionResult | Resultado técnico de ejecución |
| EvidenceManifest JSON | EvidenceChain / EvidenceManifest | Prueba verificable del ciclo |
| AuditDecision JSON | OwnerDecision / CoreDecision | Decisión auditable post-proceso |
| HumanEscalation JSON | OwnerClarification / HumanRequired | Escalación mínima solo cuando corresponde |

---

## 4. Regla de no contaminación

La factoría puede construir SmartPyme, pero no debe contaminar el producto con su propio runtime.

```text
factory/**    → gobierna construcción, tareas, agentes, evidencia de desarrollo.
app/**        → runtime del producto SmartPyme.
docs/factory/ → protocolos de construcción.
docs/product/ → arquitectura y contratos del producto.
```

Si una TaskSpec de factoría intenta modificar producto sin frente activo explícito:

```json
{
  "decision": "BLOCKED",
  "blocking_reason": "BLOCKED_SCOPE_DRIFT"
}
```

---

## 5. Capa por capa

El Blueprint organiza SmartPyme por capas funcionales.

La factoría debe operar con la misma disciplina:

```text
1. Concepto
2. Contrato JSON/Pydantic
3. Servicio determinístico
4. Persistencia
5. Orquestación
6. Evidencia
7. Owner/Human-in-the-Loop
```

Ninguna implementación grande debe saltar directamente de concepto a runtime.

---

## 6. Qué se reutiliza del Blueprint

Del Blueprint Técnico se adoptan como lenguaje de referencia:

```text
IngestPayload
OwnerDecision
EvidenceChain
JobLifecycle
Hard Core determinístico
AI Layer interpretativo
Pydantic como frontera sagrada
Owner Layer como soberanía humana
```

Estos términos deben alimentar futuros contratos, no necesariamente archivos de código inmediatos.

---

## 7. Hitos recomendados después de esta alineación

```text
HITO 07 — Definir contrato Product IngestPayload v1 sin implementación.
HITO 08 — Definir contrato EvidenceChain v1 sin implementación.
HITO 09 — Definir contrato OwnerDecision v1 sin implementación.
HITO 10 — Recién después, seleccionar una capa producto para implementación mínima.
```

---

## 8. Cierre

La factoría ya ejecuta ciclos soberanos.

El Blueprint aporta la brújula de producto.

La regla operativa queda:

```text
La factoría produce SmartPyme capa por capa.
Cada capa empieza por JSON/Pydantic.
Cada ejecución deja evidencia.
Cada decisión humana queda explícita.
```
