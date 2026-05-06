# FACTORY_V2_TOOLING_CONFIG_GUIDE

Estado: GUIA OPERATIVA INICIAL  
Fecha: 2026-05-06  
Rama: `factory/ts-006-jobs-sovereign-persistence`

---

## VEREDICTO

Esta guía fija la configuración operativa mínima de la pila SmartPyme Factory V2.

Objetivo:

```text
Reducir ambigüedad operativa antes de introducir LangGraph, Prefect y Pydantic AI.
```

La guía está alineada con:

```text
docs/factory/BLUEPRINT_001_FACTORIA_LOW_COST_MULTIAGENTE.md
docs/factory/FACTORY_V2_STATUS.md
docs/factory/FACTORY_V2_CONTRACTS.md
docs/factory/CHATGPT_OPERATING_CONTRACT.md
```

Regla base:

```text
Docker ejecuta.
Pydantic valida.
LangGraph orquesta estado.
Prefect hace durable el workflow.
Pydantic AI tipa agentes.
Hermes gobierna HITL/gateway.
Vertex provee modelos gestionados.
GitHub es fuente de verdad.
```

---

## PRINCIPIOS DE INTEGRACION

```text
No tocar legacy como base arquitectónica.
No continuar HITO_010/HITO_011/HITO_012 legacy.
No crecer queue_runner.py.
No convertir Docker real en default global.
No usar prompts gigantes como mecanismo operativo permanente.
No usar modelos pagos como centro permanente de la factoría.
No habilitar Pydantic AI antes de sandbox + contratos + HITL.
```

Orden sano de madurez:

```text
1. DockerSandboxAdapter validado por inyección explícita.
2. Futuro docker_runner explícito.
3. LangGraph mínimo con nodos determinísticos.
4. Hermes HITL.
5. GitHub PR plan.
6. Prefect para jobs durables.
7. Pydantic AI para agentes tipados.
```

---

## 1. Docker

### Rol en SmartPyme Factory

Docker es la única capa autorizada para ejecutar código generado.

Uso actual:

```text
DockerSandboxAdapter inyectado explícitamente en run_graph.
```

Uso futuro inmediato:

```text
factory_v2/docker_runner.py como entrada explícita para Docker real.
```

Docker no debe convertirse en default global del grafo.

---

### Configuración mínima

Dependencias del sistema:

```bash
sudo apt-get install -y docker.io python3-docker
```

El paquete clave para Python en Debian/PEP 668 es:

```text
python3-docker
```

No usar:

```text
python3 -m pip install docker
```

si el entorno está marcado como externally managed.

---

### Smoke de daemon Docker

```bash
systemctl status docker --no-pager || true
docker version || true
docker ps || true
```

Criterio PASS:

```text
docker.service active running
docker version muestra Client y Server
docker ps responde sin error
```

Criterio BLOCKED:

```text
Cannot connect to the Docker daemon
permission denied on docker.sock
Docker server ausente
```

---

### Smoke de SDK Python Docker

```bash
cd /opt/smartpyme-factory/repos/SmartPyme && \
PYTHONPATH=. python3 - <<'PY'
from factory.sandbox.docker_executor import _DOCKER_SDK_AVAILABLE, _docker_daemon_available
print("_DOCKER_SDK_AVAILABLE =", _DOCKER_SDK_AVAILABLE)
print("_docker_daemon_available =", _docker_daemon_available())
PY
```

Criterio PASS:

```text
_DOCKER_SDK_AVAILABLE = True
_docker_daemon_available = True
```

Criterio BLOCKED:

```text
_DOCKER_SDK_AVAILABLE = False
_docker_daemon_available = False
```

Acción correctiva validada:

```bash
sudo apt-get update && sudo apt-get install -y python3-docker
```

---

### Smoke real validado

Caso permitido:

```text
DockerSandboxAdapter ejecuta código permitido en Docker real.
status=PASS
return_code=0
reasons=[]
```

Caso bloqueado:

```text
CodePolicyV2 bloquea import os antes de Docker.
status=BLOCKED
return_code=125
reasons=['IMPORT_OS_BLOCKED']
```

Orden de seguridad:

```text
code/test_code
-> CodePolicyV2
-> _build_shell_command
-> CommandPolicyV2
-> DockerExecutor
-> ExecutionResultV2
```

---

### Fuentes oficiales

```text
https://docs.docker.com/engine/containers/run/
https://docs.docker.com/reference/api/engine/sdk/
https://docker-py.readthedocs.io/en/stable/containers.html
```

---

## 2. Pydantic

### Rol en SmartPyme Factory

Pydantic gobierna contratos, validación y serialización.

Contratos actuales:

```text
TaskSpecV2
ExecutionResultV2
GraphState
NodeStatus
```

Archivo:

```text
factory_v2/contracts.py
```

---

### Smoke operativo

```bash
cd /opt/smartpyme-factory/repos/SmartPyme && \
python3 - <<'PY'
from factory_v2.contracts import TaskSpecV2
spec = TaskSpecV2(task_id="SMOKE", objective="validar contrato")
print(spec.model_dump())
PY
```

Criterio PASS:

```text
Se imprime model_dump con task_id y objective.
```

Criterio BLOCKED:

```text
ImportError
ValidationError inesperado
```

---

### Uso permitido ahora

```text
Definir contratos.
Validar estados.
Serializar evidencia.
Sostener run.json y ExecutionResultV2.
```

### Uso prohibido ahora

```text
Reemplazar orquestación.
Ejecutar comandos.
Decidir aprobación humana.
```

---

### Fuentes oficiales

```text
https://docs.pydantic.dev/latest/
https://docs.pydantic.dev/latest/concepts/models/
https://docs.pydantic.dev/latest/concepts/json_schema/
```

---

## 3. LangGraph

### Rol en SmartPyme Factory

LangGraph será el orquestador stateful/multiagente futuro.

Rol previsto:

```text
Coordinar nodos.
Mantener estado.
Permitir ciclos controlados.
Habilitar pausas/HITL.
Reanudar trabajos.
```

No entra hasta cerrar la entrada explícita de Docker y runner controlado.

---

### Configuración mínima futura

```bash
python3 -m pip install langgraph
```

En esta fase no debe instalarse ni integrarse si agrega fricción.

---

### Smoke futuro sugerido

```python
from typing import TypedDict
from langgraph.graph import StateGraph, END

class State(TypedDict):
    message: str

def node(state: State) -> State:
    return {"message": state["message"] + " OK"}

workflow = StateGraph(State)
workflow.add_node("node", node)
workflow.set_entry_point("node")
workflow.add_edge("node", END)
app = workflow.compile()
print(app.invoke({"message": "LANGGRAPH"}))
```

Criterio PASS:

```text
El grafo compila y devuelve estado final.
```

Criterio BLOCKED:

```text
ImportError
Error de estado
Loop no controlado
```

---

### Uso permitido ahora

```text
Diseño documental.
Preparación de contratos.
No implementación todavía.
```

### Uso prohibido ahora

```text
Reemplazar run_graph manual antes de cerrar runner explícito.
Meter agentes reales prematuramente.
```

---

### Fuentes oficiales

```text
https://docs.langchain.com/oss/python/langgraph/overview
https://docs.langchain.com/oss/python/langgraph/persistence
```

---

## 4. Prefect

### Rol en SmartPyme Factory

Prefect será runtime durable en fase posterior.

Rol previsto:

```text
Jobs largos.
Retries.
Scheduling.
Watchdog.
Observabilidad operacional.
```

Prefect no reemplaza LangGraph.

---

### Configuración mínima futura

```bash
python3 -m pip install prefect
```

Smoke simple futuro:

```python
from prefect import flow

@flow
def smoke() -> str:
    return "PREFECT_OK"

print(smoke())
```

Criterio PASS:

```text
El flow corre y devuelve PREFECT_OK.
```

Criterio BLOCKED:

```text
ImportError
Problemas de PREFECT_API_URL si se usa servidor externo
```

---

### Uso permitido ahora

```text
Planificación documental.
No runtime principal todavía.
```

### Uso prohibido ahora

```text
Meter Prefect antes de cerrar grafo/runner.
Usarlo como orquestador cognitivo.
```

---

### Fuentes oficiales

```text
https://docs.prefect.io/
https://docs.prefect.io/latest/concepts/flows/
https://docs.prefect.io/latest/concepts/task-runners/
```

---

## 5. Pydantic AI

### Rol en SmartPyme Factory

Pydantic AI entra como capa de agentes tipados cuando ya existan:

```text
sandbox Docker validado
contratos Pydantic estables
HITL/Hermes definido
```

No debe entrar antes.

---

### Smoke permitido ahora

Como no está habilitado todavía para operación, el único smoke aceptable es import básico si se instala:

```bash
python3 - <<'PY'
import pydantic_ai
print("PYDANTIC_AI_IMPORT_OK")
PY
```

Criterio PASS:

```text
PYDANTIC_AI_IMPORT_OK
```

Criterio BLOCKED:

```text
ImportError
```

---

### Uso permitido ahora

```text
Lectura de documentación.
Diseño de contratos de tools/output.
```

### Uso prohibido ahora

```text
Agentes autónomos tocando código.
Tools sin sandbox.
Outputs sin contratos.
Acciones sin HITL.
```

---

### Fuentes oficiales

```text
https://ai.pydantic.dev/
https://ai.pydantic.dev/agents/
https://ai.pydantic.dev/output/
https://ai.pydantic.dev/tools/
```

---

## 6. Hermes

### Rol en SmartPyme Factory

Hermes es gateway operativo/HITL/control humano.

Hace:

```text
Recibe intención.
Presenta evidencia.
Pide aprobación.
Reporta estado.
Opera ciclos cortos.
```

No hace:

```text
No reemplaza LangGraph.
No ejecuta código como sandbox.
No escribe libremente.
No confirma config por introspección verbal del modelo.
```

---

### Configuración real actual

Rutas canónicas:

```text
/home/neoalmasana/.hermes/config.yaml
/home/neoalmasana/.hermes/.env
/home/neoalmasana/run-hermes-gateway.sh
/opt/smartpyme-factory/repos/hermes-agent
```

Lectura válida:

```bash
cat /home/neoalmasana/.hermes/config.yaml
cat /home/neoalmasana/.hermes/.env
```

No usar introspección verbal del modelo como fuente de verdad.

---

### Safe mode validado

Valores verificados previamente por lectura directa:

```text
agent.max_turns: 8
compression.enabled: false
terminal.persistent_shell: false
auxiliary.compression.provider: vacío
```

Uso permitido:

```text
AUDIT corto.
WRITE pequeño de 1 archivo + 1 test.
```

Uso prohibido:

```text
WRITE complejo.
Refactor largo.
Edición multi-capa.
Cambios de arquitectura.
```

---

### Smoke operativo sugerido

```bash
ls -la /home/neoalmasana/.hermes && \
head -80 /home/neoalmasana/.hermes/config.yaml
```

Criterio PASS:

```text
config.yaml existe y puede leerse.
.env existe o su ausencia se documenta.
```

Criterio BLOCKED:

```text
config.yaml ausente
YAML inválido
provider/model no resoluble
```

---

### Fuentes oficiales / límites

Fuentes externas conocidas:

```text
https://hermes-agent.nousresearch.com/docs/user-guide/configuration
https://hermes-agent.nousresearch.com/docs/integrations/providers
```

Fuente real operativa del proyecto:

```text
/opt/smartpyme-factory/repos/hermes-agent
/home/neoalmasana/.hermes/config.yaml
```

Límite:

```text
Si la documentación interna de hermes-agent no está accesible, documentar LIMITES y continuar con lectura directa de config real.
```

---

## 7. Vertex AI / Model Garden / MaaS

### Rol en SmartPyme Factory

Vertex AI provee modelos gestionados y MaaS.

Uso actual:

```text
Gemini Vertex: principal para lectura/auditoría/documentación.
Qwen3 Coder Vertex MaaS: builder puntual si no hay 429.
Kimi K2 Thinking Vertex MaaS: auditor puntual.
```

No usar en esta fase:

```text
OpenRouter/DeepSeek diario.
IA local/Ollama.
```

---

### Autenticación real validada

Flujo principal:

```bash
gcloud auth application-default login
```

o token directo:

```bash
gcloud auth print-access-token
```

No usar como flujo principal:

```text
GOOGLE_APPLICATION_CREDENTIALS
```

salvo que se defina explícitamente una cuenta de servicio.

---

### Fuentes oficiales

```text
https://cloud.google.com/vertex-ai/generative-ai/docs/
https://cloud.google.com/vertex-ai/generative-ai/docs/maas/overview
https://cloud.google.com/vertex-ai/generative-ai/docs/model-reference/inference
```

---

## 8. Gemini Vertex

### Rol actual

```text
Modelo principal estable para lectura, auditoría y documentación.
No queda habilitado para tocar código libremente.
```

Modelo operativo:

```text
gemini-2.5-pro
```

---

### Variables reales

```bash
unset GOOGLE_API_KEY GEMINI_API_KEY
export GOOGLE_GENAI_USE_VERTEXAI=true
export GOOGLE_CLOUD_PROJECT=smartseller-490511
export GOOGLE_CLOUD_LOCATION=us-central1
```

---

### Smoke validado

```bash
unset GOOGLE_API_KEY GEMINI_API_KEY && \
GOOGLE_GENAI_USE_VERTEXAI=true \
GOOGLE_CLOUD_PROJECT=smartseller-490511 \
GOOGLE_CLOUD_LOCATION=us-central1 \
gemini -m gemini-2.5-pro -p "Respondé solo: VERTEX_OK"
```

Criterio PASS:

```text
VERTEX_OK
```

Criterio BLOCKED:

```text
Auth error
Billing/quota error
Modelo no disponible
```

---

### Fuentes oficiales

```text
https://cloud.google.com/vertex-ai/generative-ai/docs/models/gemini/2-5-pro
https://cloud.google.com/vertex-ai/generative-ai/docs/learn/model-versions
```

---

## 9. Qwen3 Coder Vertex MaaS

### Rol actual

```text
Builder puntual de código si no hay 429.
No usar como modelo principal permanente.
```

Modelo validado:

```text
qwen/qwen3-coder-480b-a35b-instruct-maas
```

Región:

```text
us-south1
```

---

### Smoke validado

```bash
PROJECT_ID=smartseller-490511
REGION=us-south1
ENDPOINT=${REGION}-aiplatform.googleapis.com

curl -sS \
  -X POST \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "Content-Type: application/json" \
  "https://${ENDPOINT}/v1/projects/${PROJECT_ID}/locations/${REGION}/endpoints/openapi/chat/completions" \
  -d '{
    "model": "qwen/qwen3-coder-480b-a35b-instruct-maas",
    "stream": false,
    "messages": [
      {"role": "user", "content": "Respondé solo: QWEN_VERTEX_OK"}
    ],
    "max_tokens": 64
  }'
```

Criterio PASS validado:

```text
QWEN_VERTEX_OK
finish_reason=stop
total_tokens bajo
traffic_type=ON_DEMAND
```

Criterio BLOCKED/PARTIAL:

```text
429 Too Many Requests
RESOURCE_EXHAUSTED
modelo no disponible en región
```

---

### Fuentes oficiales

```text
https://cloud.google.com/vertex-ai/generative-ai/docs/maas/qwen/qwen3-coder
https://cloud.google.com/vertex-ai/generative-ai/docs/maas/overview
```

---

## 10. Kimi K2 Thinking Vertex MaaS

### Rol actual

```text
Auditor puntual.
No usar como builder principal.
No usar para smoke corto con max_tokens demasiado bajo.
```

Modelo validado:

```text
moonshotai/kimi-k2-thinking-maas
```

Región:

```text
global
```

Endpoint:

```text
aiplatform.googleapis.com
```

---

### Smoke validado

```bash
PROJECT_ID=smartseller-490511
REGION=global
ENDPOINT=aiplatform.googleapis.com

curl -sS \
  -X POST \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "Content-Type: application/json" \
  "https://${ENDPOINT}/v1/projects/${PROJECT_ID}/locations/${REGION}/endpoints/openapi/chat/completions" \
  -d '{
    "model": "moonshotai/kimi-k2-thinking-maas",
    "stream": false,
    "messages": [
      {"role": "user", "content": "Analizá en una frase si este canal está operativo."}
    ],
    "max_tokens": 160
  }'
```

Criterio PASS validado:

```text
Respuesta JSON del modelo.
traffic_type=ON_DEMAND.
model=moonshotai/kimi-k2-thinking-maas.
```

Nota:

```text
Kimi puede consumir tokens en reasoning_content.
Si max_tokens es bajo, puede cortar con finish_reason=length y content=null.
```

Criterio BLOCKED/PARTIAL:

```text
429 RESOURCE_EXHAUSTED
finish_reason=length con content=null
modelo no disponible en región
```

---

### Fuentes oficiales

```text
https://cloud.google.com/vertex-ai/generative-ai/docs/maas/kimi
https://cloud.google.com/vertex-ai/generative-ai/docs/maas/kimi/kimi-k2-thinking
```

---

## 11. GitHub

### Rol

GitHub es fuente de verdad del código.

Regla:

```text
Un ciclo no está cerrado hasta commit/push o documento actualizado en GitHub.
```

---

### Smoke operativo

```bash
cd /opt/smartpyme-factory/repos/SmartPyme && \
git branch --show-current && \
git status --short && \
git log -3 --oneline
```

Criterio PASS:

```text
Rama correcta.
Worktree limpio o diff esperado.
Últimos commits coinciden con estado reportado.
```

Criterio BLOCKED:

```text
Rama incorrecta.
Cambios no trackeados inesperados.
Divergencia con origin.
```

---

## 12. Tabla resumen

| Herramienta | Rol | Config mínima | Smoke test | Riesgo | Uso permitido ahora | Uso prohibido ahora |
|---|---|---|---|---|---|---|
| Docker | Sandbox / aislamiento | Docker daemon + `python3-docker` | `docker version`; `_DOCKER_SDK_AVAILABLE=True` | permisos, daemon, SDK ausente | `DockerSandboxAdapter` inyectado | default global |
| Pydantic | contratos | paquete instalado y modelos en `factory_v2/contracts.py` | instanciar `TaskSpecV2` | validaciones mal definidas | contratos/evidencia | orquestar/ejecutar |
| LangGraph | grafo stateful futuro | no activo todavía | smoke futuro de `StateGraph` | loops/deadlocks | diseño/documentación | reemplazar run_graph ahora |
| Prefect | jobs durables futuro | no activo todavía | smoke futuro `@flow` | fricción prematura | planificación | runtime principal ahora |
| Pydantic AI | agentes tipados futuro | no activo todavía | import smoke si se instala | autonomía prematura | diseño de agents/tools | tocar código sin sandbox/HITL |
| Hermes | gateway/HITL | config real en `~/.hermes` | leer `config.yaml` | config falsa por introspección | AUDIT corto / WRITE mínimo | refactor largo |
| Gemini Vertex | modelo principal estable | ADC + Vertex env vars | `VERTEX_OK` | costo/cuota | auditoría/documentación | escritura libre |
| Qwen3 Coder MaaS | builder puntual | curl OpenAI-compatible us-south1 | `QWEN_VERTEX_OK` | 429 | código puntual supervisado | modelo principal |
| Kimi K2 Thinking MaaS | auditor puntual | curl OpenAI-compatible global | JSON ON_DEMAND | reasoning largo/429 | auditoría difícil | builder principal |
| GitHub | fuente de verdad | repo/rama correctos | `git status`, `git log` | rama equivocada | commits/PRs | merge automático inicial |

---

## 13. Comandos diarios mínimos

### Estado repo

```bash
cd /opt/smartpyme-factory/repos/SmartPyme && \
git branch --show-current && \
git status --short && \
git log -3 --oneline
```

### Tests factory_v2

```bash
cd /opt/smartpyme-factory/repos/SmartPyme && \
pytest tests/factory_v2/ -q
```

### Docker

```bash
systemctl status docker --no-pager || true
docker version || true
```

### Docker SDK Python

```bash
cd /opt/smartpyme-factory/repos/SmartPyme && \
PYTHONPATH=. python3 - <<'PY'
from factory.sandbox.docker_executor import _DOCKER_SDK_AVAILABLE, _docker_daemon_available
print("_DOCKER_SDK_AVAILABLE =", _DOCKER_SDK_AVAILABLE)
print("_docker_daemon_available =", _docker_daemon_available())
PY
```

### Hermes config real

```bash
cat /home/neoalmasana/.hermes/config.yaml
```

### Gemini Vertex

```bash
unset GOOGLE_API_KEY GEMINI_API_KEY && \
GOOGLE_GENAI_USE_VERTEXAI=true \
GOOGLE_CLOUD_PROJECT=smartseller-490511 \
GOOGLE_CLOUD_LOCATION=us-central1 \
gemini -m gemini-2.5-pro -p "Respondé solo: VERTEX_OK"
```

---

## LIMITES

```text
Hermes depende de config real local y puede diferir de documentación pública.
Qwen3 Coder MaaS puede responder 429.
Kimi K2 Thinking MaaS puede consumir tokens en reasoning_content y devolver content=null si max_tokens es bajo.
Gemini Vertex está habilitado para lectura/auditoría/documentación, no para escritura libre.
Ollama/IA local queda descartada temporalmente por costo/beneficio.
Prefect, LangGraph y Pydantic AI aún no están activos en runtime factory_v2.
```

---

## DECISION FINAL

La pila Factory V2 debe crecer por capas:

```text
Docker validado
-> runner explícito
-> LangGraph determinístico
-> Hermes HITL
-> GitHub PR plan
-> Prefect durable
-> Pydantic AI tipado
```

La regla rectora se mantiene:

```text
Agentes intercambiables, contratos estrictos, Docker obligatorio, GitHub visible, humano aprueba.
```
