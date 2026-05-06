# FACTORY_V2_STATUS

Estado: CANONICO v5  
Fecha: 2026-05-06  
Rama: `factory/ts-006-jobs-sovereign-persistence`  
HEAD validado: `5cdec6c feat(factory-v2): enforce code policy before docker wrapper`

---

## VEREDICTO

`factory_v2` está en estado funcional mínimo validado.

La POC determinística low-cost ya tiene:

- contratos mínimos;
- grafo determinístico;
- sandbox fake;
- adapter Docker real inyectable;
- evidencia por nodo;
- evidencia de run (`run.json`);
- documentación de contratos;
- `CommandPolicyV2`;
- `CodePolicyV2`;
- enforcement de `CodePolicyV2` antes de construir el wrapper Docker;
- enforcement de `CommandPolicyV2` sobre el wrapper Docker;
- smoke real de `DockerSandboxAdapter` validado;
- smoke de `run_graph` con `DockerSandboxAdapter` inyectado validado;
- suite `tests/factory_v2/` verde.

---

## TEST RESULT

Últimas validaciones reportadas:

```text
pytest tests/factory_v2/test_docker_sandbox_adapter.py -q
............ [100%]

pytest tests/factory_v2/ -q
........................................... [100%]
```

Validaciones parciales registradas:

```text
pytest tests/factory_v2/test_policy.py -q
...... [100%]
6 passed

pytest tests/factory_v2/test_code_policy.py -q
PASS
```

---

## SMOKE REAL DOCKER + POLICIES

Fecha: 2026-05-06  
Modo: smoke manual, sin tocar código ni `graph.py`.

### Precondición corregida

Después del cambio/reinicio de instancia, Docker daemon estaba activo, pero Python no detectaba Docker porque faltaba SDK:

```text
_DOCKER_SDK_AVAILABLE = False
_docker_daemon_available = False
```

Se instaló dependencia del sistema:

```text
sudo apt-get install -y python3-docker
```

Resultado:

```text
_DOCKER_SDK_AVAILABLE = True
_docker_daemon_available = True
```

### Smoke permitido

Entrada:

```text
task_id: manual_docker_policy_pass
code: def add(a, b): return a + b
test_code: assert add(1, 2) == 3
```

Resultado:

```text
status=PASS
return_code=0
reasons=[]
```

Conclusión:

```text
DockerSandboxAdapter ejecuta código permitido en Docker real.
```

### Smoke bloqueado por CodePolicyV2

Entrada:

```text
task_id: manual_docker_code_policy_block
code: import os
test_code: vacío
```

Resultado:

```text
status=BLOCKED
return_code=125
reasons=['IMPORT_OS_BLOCKED']
stderr='Código bloqueado por la política de contenido.'
```

Conclusión:

```text
CodePolicyV2 bloquea contenido peligroso antes de construir/ejecutar el wrapper Docker.
```

---

## SMOKE RUN_GRAPH + DOCKER ADAPTER INYECTADO

Fecha: 2026-05-06  
Modo: smoke manual, sin tocar código ni legacy.

Ejecución:

```text
run_graph(
  TaskSpecV2(task_id="manual_run_graph_docker_adapter", ...),
  sandbox_adapter=DockerSandboxAdapter(),
)
```

Resultado del estado:

```text
halted: False
halt_reason: vacío
audit: PASS
implement: PASS
sandbox: PASS
review: PASS
sandbox_reasons: []
review_return_code: 0
```

Evidencia generada:

```text
factory_v2/evidence/manual_run_graph_docker_adapter/audit_20260506T173749Z.json
factory_v2/evidence/manual_run_graph_docker_adapter/implement_20260506T173749Z.json
factory_v2/evidence/manual_run_graph_docker_adapter/sandbox_20260506T173749Z.json
factory_v2/evidence/manual_run_graph_docker_adapter/review_20260506T173749Z.json
factory_v2/evidence/manual_run_graph_docker_adapter/run.json
```

`run.json` confirmado:

```json
{
  "task_id": "manual_run_graph_docker_adapter",
  "status": "PASS",
  "halted": false,
  "halt_reason": null,
  "nodes": {
    "audit_result": "PASS",
    "implement_result": "PASS",
    "sandbox_result": "PASS",
    "review_result": "PASS"
  }
}
```

Conclusión:

```text
run_graph puede ejecutarse con DockerSandboxAdapter real por inyección explícita, sin convertir Docker en default global.
```

---

## COMMITS RELEVANTES

```text
5cdec6c feat(factory-v2): enforce code policy before docker wrapper
16984fe test(factory-v2): fix socket policy coverage
21343ef test(factory-v2): cover code policy
32e447a feat(factory-v2): add code policy
32d8925 feat(factory-v2): enforce command policy in docker sandbox
f7d13c2 feat(factory-v2): add command policy
66057d5 docs(factory): add factory_v2 contracts
5cbeca3 docs(factory): record factory_v2 status
eac84e3 feat(factory-v2): write run evidence from graph
0e729d3 feat(factory-v2): add run evidence writer
ba7f6db test(factory-v2): cover evidence writer
f3b0fe7 feat(factory-v2): allow sandbox adapter injection
439b3d0 feat(factory-v2): add docker sandbox adapter
04e7794 feat(factory-v2): add low-cost deterministic scaffold
```

---

## COMPONENTES IMPLEMENTADOS

### Contratos

Archivo:

```text
factory_v2/contracts.py
```

Incluye:

- `TaskSpecV2`;
- `ExecutionResultV2`;
- `GraphState`;
- `NodeStatus`.

Estado:

```text
VALIDADO
```

---

### Documentación de contratos

Archivo:

```text
docs/factory/FACTORY_V2_CONTRACTS.md
```

Documenta:

- contratos Pydantic;
- `EvidenceWriter.write`;
- `EvidenceWriter.write_run`;
- payload de `run.json`;
- `SandboxAdapterProtocol`;
- `FakeSandboxAdapter`;
- `DockerSandboxAdapter`;
- flujo normal;
- halt temprano;
- límites actuales.

Estado:

```text
VALIDADO
```

---

### Grafo determinístico

Archivo:

```text
factory_v2/graph.py
```

Flujo actual:

```text
audit -> implement -> sandbox -> review
```

Características:

- sin LLM;
- determinístico;
- acepta adapter de sandbox inyectable;
- soporta flujo normal;
- soporta halt temprano;
- escribe evidencia por nodo;
- escribe `run.json` por ejecución.

Estado:

```text
VALIDADO CON FAKE SANDBOX Y CON DOCKER ADAPTER INYECTADO
```

---

### CommandPolicyV2

Archivo:

```text
factory_v2/policy.py
```

Rol:

```text
Política determinística mínima para evaluar comandos antes de ejecución en sandbox Docker.
```

Contrato:

- allowlist mínima;
- blocklist de comandos destructivos, red, shell, escalada y contenedores;
- fail-closed para comandos desconocidos;
- razones claras.

Límite:

```text
En DockerSandboxAdapter evalúa el wrapper generado, no el contenido semántico de code/test.
```

Estado:

```text
VALIDADO
```

---

### CodePolicyV2

Archivo:

```text
factory_v2/code_policy.py
```

Rol:

```text
Política determinística mínima para validar code/test_code antes de construir el wrapper Docker.
```

Contrato:

- fail-closed si `code` está vacío;
- bloquea patrones peligrosos de IO, red, procesos y ejecución dinámica;
- evalúa `code` y `test_code`;
- devuelve razones estables como `IMPORT_OS_BLOCKED`, `SUBPROCESS_BLOCKED`, `SOCKET_BLOCKED`, `OPEN_BLOCKED`, `EVAL_BLOCKED`, `EXEC_BLOCKED`, `DYNAMIC_IMPORT_BLOCKED`.

Límite:

```text
No reemplaza sandbox real ni análisis estático profundo.
```

Estado:

```text
VALIDADO
```

---

### DockerSandboxAdapter

Archivo:

```text
factory_v2/sandbox.py
```

Rol:

```text
Wrapper de DockerExecutor real detrás del contrato factory_v2.
```

Orden de seguridad actual:

```text
code/test_code
-> CodePolicyV2
-> _build_shell_command
-> CommandPolicyV2
-> DockerExecutor
-> ExecutionResultV2
```

Casos cubiertos:

- comando seguro con PASS;
- comando bloqueado por executor legacy;
- fallo de comando;
- Docker no disponible;
- mapeo hacia `ExecutionResultV2`;
- bloqueo por `CodePolicyV2` antes de construir wrapper;
- bloqueo por `CommandPolicyV2` antes de invocar DockerExecutor;
- no invocación del executor cuando alguna policy bloquea.

Estado:

```text
VALIDADO COMO ADAPTER INYECTABLE CON CODE POLICY, COMMAND POLICY, SMOKE REAL DOCKER Y SMOKE RUN_GRAPH
```

Regla:

```text
Docker real no queda como default global del grafo.
Se usa por inyección explícita.
```

---

### EvidenceWriter

Archivo:

```text
factory_v2/evidence.py
```

Funciones validadas:

```text
EvidenceWriter.write
EvidenceWriter.write_run
```

Estado:

```text
VALIDADO
```

---

## REGLAS RESPETADAS

```text
No tocar app/**
No tocar factory/core/**
No tocar queue_runner.py
No continuar HITO_010/HITO_011/HITO_012 legacy
No mezclar factory_v2 con legacy
No usar LLM dentro del grafo
No hacer Docker default sin inyección explícita
```

---

## ESTADO DE HERMES / MODELOS

Política operativa actual:

```text
Gemini Vertex: principal para lectura, auditoría y documentación.
Qwen3 Coder Vertex MaaS: builder puntual si no hay 429.
Kimi K2 Thinking Vertex MaaS: auditor puntual.
OpenRouter/DeepSeek: no diario por costo/límites.
IA local/Ollama: descartada para esta fase por costo/beneficio.
Patches críticos: manuales y determinísticos.
```

---

## FRONTERA ACTUAL

`factory_v2` ya puede ejecutar una POC determinística con evidencia mínima y Docker adapter protegido por dos capas de política, tanto en smoke directo como inyectado en `run_graph`.

Todavía no tiene:

- LangGraph real;
- agentes reales;
- integración Hermes Runtime;
- Prefect;
- PR automation;
- policy engine completo;
- análisis estático profundo;
- persistencia industrial;
- observabilidad industrial;
- factory-of-factories.

---

## PRÓXIMOS CICLOS RECOMENDADOS

### Ciclo 1 — Test automatizado de run_graph con Docker adapter inyectado

Objetivo:

```text
Convertir el smoke manual de run_graph + DockerSandboxAdapter en test explícito si aporta valor.
```

Condición:

```text
No convertir Docker real en default global.
Evitar test frágil si Docker no está disponible en CI.
```

---

### Ciclo 2 — Integración explícita de Docker en grafo bajo control

Objetivo:

```text
Agregar mecanismo explícito para ejecutar run_graph con DockerSandboxAdapter solo por inyección/control deliberado.
```

Condición:

```text
No convertir Docker real en default global.
```

---

### Ciclo 3 — LangGraph real mínimo

Objetivo:

```text
Reemplazar grafo manual por LangGraph manteniendo los contratos actuales.
```

Condición previa:

```text
No romper tests existentes.
```

---

## DECISIÓN FINAL

`factory_v2` queda como nueva base limpia para continuar la factoría low-cost multiagente.

El legacy queda como cantera técnica y evidencia histórica, no como centro de la nueva arquitectura.

Frase rectora:

```text
Factory_v2 avanza por ciclos cortos, contratos explícitos, evidencia, políticas mínimas, sandbox real validado, run_graph validado y tests verdes.
```
