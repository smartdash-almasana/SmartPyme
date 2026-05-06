# FACTORY_V2_STATUS

Estado: CANONICO v1  
Fecha: 2026-05-06  
Rama: `factory/ts-006-jobs-sovereign-persistence`  
HEAD validado: `eac84e3 feat(factory-v2): write run evidence from graph`

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
- suite `tests/factory_v2/` verde.

---

## TEST RESULT

Última validación reportada:

```text
pytest tests/factory_v2/ -q
......................... [100%]
25 passed
```

Worktree reportado como limpio después de la ejecución.

---

## COMMITS RELEVANTES

```text
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
VALIDADO COMO ADAPTER INYECTABLE
```

Cobertura:

```text
tests/factory_v2/test_docker_sandbox_adapter.py
```

Casos cubiertos:

- comando seguro con PASS;
- comando bloqueado;
- fallo de comando;
- Docker no disponible;
- mapeo de resultado hacia `ExecutionResultV2`.

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

El grafo ahora escribe `run.json` al final de cada ejecución.

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

## ESTADO DE HERMES

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

Uso permitido de Hermes por ahora:

```text
AUDIT corto
WRITE pequeño de 1 archivo + 1 test
```

Uso no recomendado todavía:

```text
WRITE complejo
edición de múltiples capas
refactor largo
cambios de arquitectura
```

---

## FRONTERA ACTUAL

`factory_v2` ya puede ejecutar una POC determinística con evidencia mínima.

Todavía no tiene:

- LangGraph real;
- agentes reales;
- integración Hermes Runtime;
- Prefect;
- PR automation;
- policy engine completo;
- persistencia industrial;
- observabilidad industrial;
- factory-of-factories.

---

## PRÓXIMOS CICLOS RECOMENDADOS

### Ciclo 1 — Documentar contratos actuales

Objetivo:

```text
Documentar contratos internos factory_v2 y payload de run.json.
```

Archivo sugerido:

```text
docs/factory/FACTORY_V2_CONTRACTS.md
```

---

### Ciclo 2 — Política de comandos mínima

Objetivo:

```text
Agregar CommandPolicyV2 mínima antes de permitir Docker real operativo.
```

Archivos probables:

```text
factory_v2/policy.py
tests/factory_v2/test_policy.py
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
Factory_v2 avanza por ciclos cortos, contratos explícitos, evidencia y tests verdes.
```
