# FACTORY_V2_STATUS

Estado: CANONICO v10  
Fecha: 2026-05-06  
Rama: `factory/ts-006-jobs-sovereign-persistence`  
HEAD validado: `dfde069 test(factory-v2): cover minimal langgraph runner`

---

## VEREDICTO

`factory_v2` queda en estado funcional mínimo validado con:

- contratos mínimos Pydantic;
- grafo determinístico actual `run_graph`;
- sandbox fake como default seguro;
- adapter Docker real inyectable;
- runner Docker explícito `run_with_docker`;
- smoke real de Docker + policies;
- smoke real de `run_graph` con Docker inyectado;
- smoke real de `run_with_docker`;
- LangGraph probado primero en entorno aislado;
- LangGraph declarado como dependencia dev/opcional;
- runner LangGraph mínimo `run_with_langgraph`;
- evidencia por nodo;
- evidencia de run (`run.json`);
- suite `tests/factory_v2/` verde.

---

## TEST RESULT

Última validación reportada en VM:

```text
PYTHONPATH=. pytest tests/factory_v2/test_langgraph_runner.py -q
PASS

PYTHONPATH=. pytest tests/factory_v2/ -q
PASS

git status --short
limpio
```

Warning observado durante LangGraph:

```text
LangChainPendingDeprecationWarning sobre allowed_objects en JsonPlusSerializer.
```

Clasificación:

```text
No bloqueante. Advertencia de deprecación futura, no fallo de test.
```

---

## LANGGRAPH RUNNER MINIMO INTEGRADO

Fecha: 2026-05-06  
Modo: integración mínima, determinística, sin agentes reales, sin reemplazar `run_graph`.

Archivos:

```text
factory_v2/langgraph_runner.py
tests/factory_v2/test_langgraph_runner.py
```

Commits:

```text
e88898f feat(factory-v2): add minimal langgraph runner
dfde069 test(factory-v2): cover minimal langgraph runner
```

Contrato implementado:

```text
run_with_langgraph(
    task_spec: TaskSpecV2,
    sandbox_adapter: Optional[SandboxAdapterProtocol] = None,
) -> GraphState
```

Diseño:

```text
StateGraph(LangGraphRunnerState)
-> nodo único determinístico run_graph
-> END
```

Regla preservada:

```text
No reemplaza run_graph.
No introduce agentes reales.
No cambia el default seguro de run_graph.
Solo valida integración mínima con LangGraph.
```

Manejo de dependencia:

```text
Si langgraph no está instalado, run_with_langgraph levanta RuntimeError explícito.
El test usa pytest.importorskip("langgraph").
```

Validación:

```text
El test ejecuta run_with_langgraph con FakeSandboxAdapter.
Confirma GraphState.
Confirma audit_result PASS.
Confirma implement_result PASS.
Confirma sandbox_result PASS.
Confirma review_result PASS.
```

Límites:

```text
El runner LangGraph todavía delega en run_graph.
No modela audit/implement/sandbox/review como nodos LangGraph separados.
No usa checkpoints/persistencia LangGraph.
No usa HITL.
No usa agentes.
```

---

## LANGGRAPH DEPENDENCIA DEV/OPCIONAL

Archivo:

```text
pyproject.toml
```

Commit:

```text
0aa9118 build(factory-v2): declare langgraph dev dependency
```

Declaración:

```text
[project.optional-dependencies]
dev = [
  "pytest>=8.0",
  "ruff>=0.8",
  "langgraph>=1.1,<2",
]
```

Regla:

```text
LangGraph queda disponible como dependencia dev/opcional.
No reemplaza run_graph.
No entra como runtime principal todavía.
No introduce agentes reales.
```

Nota operativa:

```text
python3 -m pip install -e ".[dev]" falló por layout plano con múltiples paquetes top-level.
No se considera fallo de LangGraph.
Para validación se usó .venv-langgraph temporal + PYTHONPATH=.
El entorno temporal fue eliminado y el worktree quedó limpio.
```

---

## SMOKES CERRADOS

### Docker + policies

```text
DockerSandboxAdapter ejecuta código permitido en Docker real.
CodePolicyV2 bloquea import os antes de Docker.
CommandPolicyV2 se mantiene sobre el wrapper Docker.
```

### run_graph + DockerSandboxAdapter

```text
run_graph(..., sandbox_adapter=DockerSandboxAdapter()) termina PASS.
Evidencia por nodo y run.json confirmados.
```

### run_with_docker

```text
run_with_docker(TaskSpecV2(...)) termina PASS.
run.json confirma audit/implement/sandbox/review PASS.
```

### LangGraph aislado

```text
.venv-langgraph
langgraph==1.1.10
StateGraph mínimo audit -> review -> END
Salida: {'message': 'LANGGRAPH_SMOKE -> audit -> review'}
```

### LangGraph integrado mínimo

```text
run_with_langgraph(TaskSpecV2(...), sandbox_adapter=FakeSandboxAdapter()) termina PASS.
```

---

## COMPONENTES IMPLEMENTADOS

| Componente | Archivo | Estado |
|---|---|---|
| Contratos | `factory_v2/contracts.py` | VALIDADO |
| Evidencia | `factory_v2/evidence.py` | VALIDADO |
| Grafo determinístico | `factory_v2/graph.py` | VALIDADO |
| Sandbox fake | `factory_v2/sandbox.py` | VALIDADO |
| DockerSandboxAdapter | `factory_v2/sandbox.py` | VALIDADO |
| CommandPolicyV2 | `factory_v2/policy.py` | VALIDADO |
| CodePolicyV2 | `factory_v2/code_policy.py` | VALIDADO |
| Docker runner | `factory_v2/docker_runner.py` | VALIDADO |
| LangGraph runner | `factory_v2/langgraph_runner.py` | VALIDADO MINIMO |
| Tooling guide | `docs/factory/FACTORY_V2_TOOLING_CONFIG_GUIDE.md` | VALIDADO COMO GUIA INICIAL |

---

## COMMITS RELEVANTES

```text
dfde069 test(factory-v2): cover minimal langgraph runner
e88898f feat(factory-v2): add minimal langgraph runner
eedf62f docs(factory): record langgraph dev dependency
0aa9118 build(factory-v2): declare langgraph dev dependency
291f26b docs(factory): record langgraph isolated smoke
7a624d4 docs(factory): record run with docker smoke
74dccfc docs(factory): record explicit docker runner
2692252 test(factory-v2): cover explicit docker runner
69d8755 feat(factory-v2): add explicit docker runner
d7e7215 docs(factory): add tooling config guide
5cdec6c feat(factory-v2): enforce code policy before docker wrapper
16984fe test(factory-v2): fix socket policy coverage
21343ef test(factory-v2): cover code policy
32e447a feat(factory-v2): add code policy
32d8925 feat(factory-v2): enforce command policy in docker sandbox
f7d13c2 feat(factory-v2): add command policy
66057d5 docs(factory): add factory_v2 contracts
eac84e3 feat(factory-v2): write run evidence from graph
0e729d3 feat(factory-v2): add run evidence writer
ba7f6db test(factory-v2): cover evidence writer
f3b0fe7 feat(factory-v2): allow sandbox adapter injection
439b3d0 feat(factory-v2): add docker sandbox adapter
04e7794 feat(factory-v2): add low-cost deterministic scaffold
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
No reemplazar run_graph por LangGraph todavía
No introducir agentes reales todavía
```

---

## FRONTERA ACTUAL

`factory_v2` ya puede ejecutar una POC determinística con evidencia mínima y Docker adapter protegido por dos capas de política, tanto en smoke directo como inyectado en `run_graph`, vía runner explícito `run_with_docker`, y vía runner LangGraph mínimo que delega en `run_graph`.

Todavía no tiene:

- nodos LangGraph reales separados por etapa;
- checkpoints/persistencia LangGraph;
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

## PROXIMOS CICLOS RECOMENDADOS

### Ciclo 1 — LangGraph por nodos reales separados

Objetivo:

```text
Modelar audit -> implement -> sandbox -> review como nodos LangGraph separados, manteniendo contratos actuales.
```

Condición previa:

```text
No romper tests existentes.
No meter agentes reales.
No reemplazar run_graph hasta validar equivalencia.
```

### Ciclo 2 — Hermes HITL mínimo

Objetivo:

```text
Definir cómo Hermes aprueba/deniega una tarea antes de escalar autonomía.
```

Condición previa:

```text
Sandbox + contratos + runner explícito + LangGraph mínimo ya cerrados.
```

### Ciclo 3 — GitHub PR plan

Objetivo:

```text
Definir branch/diff/PR draft o PR simulado sin merge automático.
```

---

## DECISION FINAL

`factory_v2` queda como nueva base limpia para continuar la factoría low-cost multiagente.

Frase rectora:

```text
Factory_v2 avanza por ciclos cortos, contratos explícitos, evidencia, políticas mínimas, sandbox real validado, run_graph validado, docker_runner explícito validado, LangGraph integrado mínimamente y tests verdes.
```
