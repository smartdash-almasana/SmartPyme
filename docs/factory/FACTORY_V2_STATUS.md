# FACTORY_V2_STATUS

Estado: CANONICO v3  
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
- política mínima de comandos (`CommandPolicyV2`);
- política mínima de contenido Python (`CodePolicyV2`);
- enforcement de `CodePolicyV2` antes de construir el wrapper Docker;
- enforcement de `CommandPolicyV2` sobre el wrapper Docker;
- suite `tests/factory_v2/` verde.

---

## TEST RESULT

Última validación reportada:

```text
pytest tests/factory_v2/test_docker_sandbox_adapter.py -q
............ [100%]

pytest tests/factory_v2/ -q
........................................... [100%]
```

Validaciones previas registradas:

```text
pytest tests/factory_v2/test_policy.py -q
...... [100%]
6 passed

pytest tests/factory_v2/test_code_policy.py -q
PASS

pytest tests/factory_v2/test_docker_sandbox_adapter.py -q
........... [100%]
11 passed
```

Worktree reportado como limpio después de los ciclos cerrados.

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

Incluye contratos mínimos para:

- `TaskSpecV2`;
- `ExecutionResultV2`;
- `GraphState`;
- `NodeStatus`.

Estado:

```text
VALIDADO
```

Cobertura:

```text
tests/factory_v2/test_contracts.py
```

---

### Documentación de contratos

Archivo:

```text
docs/factory/FACTORY_V2_CONTRACTS.md
```

Estado:

```text
VALIDADO
```

Contenido documentado:

- `TaskSpecV2`;
- `ExecutionResultV2`;
- `GraphState`;
- `NodeStatus`;
- `EvidenceWriter.write`;
- `EvidenceWriter.write_run`;
- payload de `run.json`;
- `SandboxAdapterProtocol`;
- `FakeSandboxAdapter`;
- `DockerSandboxAdapter`;
- flujo normal;
- halt temprano;
- límites actuales.

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

Estado:

```text
VALIDADO
```

Características:

- sin LLM;
- determinístico;
- acepta adapter de sandbox inyectable;
- soporta flujo normal;
- soporta halt temprano;
- escribe evidencia por nodo;
- escribe `run.json` por ejecución.

Cobertura:

```text
tests/factory_v2/test_factory_graph_smoke.py
```

---

### Sandbox fake

Archivo:

```text
factory_v2/sandbox.py
```

Componente:

```text
FakeSandboxAdapter
```

Uso:

- default seguro del grafo;
- smoke tests;
- ejecución determinística sin Docker real.

Estado:

```text
VALIDADO
```

---

### CommandPolicyV2

Archivo:

```text
factory_v2/policy.py
```

Componente:

```text
CommandPolicyV2
```

Rol:

Política determinística mínima para evaluar comandos antes de ejecución en sandbox Docker.

Estado:

```text
VALIDADO
```

Cobertura:

```text
tests/factory_v2/test_policy.py
```

Contrato actual:

- allowlist mínima de comandos seguros;
- blocklist de comandos destructivos, de red, shell, escalada y contenedores;
- fail-closed para comandos desconocidos;
- razones claras para permitir o bloquear.

Límite explícito:

```text
La política evalúa el comando recibido. En DockerSandboxAdapter evalúa el wrapper generado, no el contenido semántico de code/test.
```

---

### CodePolicyV2

Archivo:

```text
factory_v2/code_policy.py
```

Componente:

```text
CodePolicyV2
```

Rol:

Política determinística mínima para validar `code` y `test_code` antes de construir el wrapper Docker.

Estado:

```text
VALIDADO
```

Cobertura:

```text
tests/factory_v2/test_code_policy.py
```

Contrato actual:

- fail-closed si `code` está vacío;
- bloquea patrones peligrosos de IO, red, procesos y ejecución dinámica;
- evalúa tanto `code` como `test_code`;
- devuelve razones estables como `IMPORT_OS_BLOCKED`, `SUBPROCESS_BLOCKED`, `SOCKET_BLOCKED`, `OPEN_BLOCKED`, `EVAL_BLOCKED`, `EXEC_BLOCKED`, `DYNAMIC_IMPORT_BLOCKED`.

Límite explícito:

```text
CodePolicyV2 es una barrera previa conservadora. No reemplaza sandbox real ni análisis estático profundo.
```

---

### DockerSandboxAdapter

Archivo:

```text
factory_v2/sandbox.py
```

Componente:

```text
DockerSandboxAdapter
```

Rol:

Wrapper de `DockerExecutor` real detrás del contrato `factory_v2`.

Estado:

```text
VALIDADO COMO ADAPTER INYECTABLE CON CODE POLICY Y COMMAND POLICY
```

Cobertura:

```text
tests/factory_v2/test_docker_sandbox_adapter.py
```

Casos cubiertos:

- comando seguro con PASS;
- comando bloqueado por executor legacy;
- fallo de comando;
- Docker no disponible;
- mapeo de resultado hacia `ExecutionResultV2`;
- policy opcional inyectada;
- bloqueo por `CodePolicyV2` antes de construir wrapper Docker;
- bloqueo por `CommandPolicyV2` antes de invocar DockerExecutor;
- no invocación del executor cuando `CodePolicyV2` bloquea;
- no invocación del executor cuando `CommandPolicyV2` bloquea.

Orden de seguridad actual:

```text
code/test_code
-> CodePolicyV2
-> _build_shell_command
-> CommandPolicyV2
-> DockerExecutor
-> ExecutionResultV2
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

Cobertura:

```text
tests/factory_v2/test_evidence_writer.py
```

`write`:

- guarda un `ExecutionResultV2` como JSON.

`write_run`:

- guarda `run.json` por `task_id`;
- conserva payload mínimo de ejecución.

---

## EVIDENCIA DE RUN

El grafo escribe `run.json` al final de cada ejecución.

Payload mínimo esperado:

```text
task_id
status
halted
halt_reason
nodes
```

Caminos cubiertos:

```text
PASS normal
BLOCKED por halt temprano
```

Estado:

```text
VALIDADO
```

---

## REGLAS RESPETADAS

Durante este ciclo se respetó:

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

Hermes fue estabilizado parcialmente para ciclos cortos.

Validaciones realizadas:

```text
AUDIT corto: PASS
WRITE trivial: PASS
WRITE pequeño real: PASS
```

Configuración real verificada en:

```text
/home/neoalmasana/.hermes/config.yaml
```

Valores safe-mode verificados por lectura directa del archivo:

```text
agent.max_turns: 8
compression.enabled: false
terminal.persistent_shell: false
auxiliary.compression.provider: vacío
```

Advertencia:

```text
No confiar en introspección verbal del modelo para confirmar config.
La verificación válida es lectura directa de config.yaml.
```

Política operativa actual de modelos:

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

`factory_v2` ya puede ejecutar una POC determinística con evidencia mínima y Docker adapter protegido por dos capas de política.

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

### Ciclo 1 — Smoke real de DockerSandboxAdapter con políticas

Objetivo:

```text
Ejecutar DockerSandboxAdapter real con caso permitido y caso bloqueado, sin convertir Docker en default global.
```

Condición:

```text
No tocar graph.py.
No tocar legacy.
Solo smoke/manual o test específico si hace falta.
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
Factory_v2 avanza por ciclos cortos, contratos explícitos, evidencia, políticas mínimas, sandbox y tests verdes.
```
