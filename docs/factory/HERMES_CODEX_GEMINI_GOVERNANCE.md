# HERMES + CODEX + GEMINI GOVERNANCE — SmartPyme Factory

## Estado

CANONICO v3 — actualizado 2026-05-06.

Este documento reemplaza la versión v2 que declaraba DeepSeek v3.2 como agente operativo primario.

La configuración operativa actual debe leerse junto con:

```text
docs/factory/HERMES_RUNTIME_CANONICAL_CONFIG.md
```

---

## VEREDICTO

Para la etapa actual de SmartPyme Factory, Hermes debe operar con:

```text
MODEL_REAL: google/gemini-2.5-pro
PROVIDER_REAL: gemini
```

Si Hermes reporta otro modelo, la salida no debe usarse para WRITE.

---

## Principio rector

Hermes es gateway operativo y HITL.

Hermes no es el orquestador central de la nueva factoría.

La nueva arquitectura apunta a:

```text
Hermes = intención humana / aprobación / consola
LangGraph = orquestación multiagente
Pydantic = contratos
Docker = ejecución segura
GitHub = PR y versionado
Prefect = jobs durables en fase posterior
```

---

## Roles actuales

### Gemini 2.5 Pro — modelo operativo actual de Hermes

Debe hacer:

- auditoría;
- diseño;
- revisión documental;
- análisis de blueprint;
- verificación de consistencia;
- tareas cortas de lectura controlada.

No debe hacer:

- implementar cambios largos;
- arreglar suites completas;
- iterar sin límite;
- tocar repo sin `WRITE_AUTHORIZED`;
- aprobar su propio trabajo final.

Regla obligatoria:

```text
MODEL_REAL debe reportar google/gemini-2.5-pro antes de trabajar.
```

---

### DeepSeek v4 Pro — implementador técnico bajo demanda

Debe hacer:

- generación de código acotada;
- refactors pequeños;
- diagnóstico de tests;
- patches delimitados por TaskSpec.

No debe hacer:

- operar si el runtime cae a DeepSeek v3.2;
- definir arquitectura final;
- modificar repo sin autorización;
- revisar su propio patch como autoridad final.

Regla obligatoria:

```text
MODEL_REAL debe coincidir con deepseek/deepseek-v4-pro si se solicita v4-pro.
```

---

### Codex — builder externo opcional

Debe hacer:

- trabajar en tareas de coding delimitadas;
- producir diff verificable;
- operar en rama/worktree aislado;
- entregar tests y evidencia.

No debe hacer:

- controlar el flujo de la factoría;
- decidir arquitectura de negocio;
- mergear directo;
- operar sin contrato.

---

### Hermes Gateway — plataforma humana

Debe hacer:

- recibir intención del owner;
- mostrar evidencia;
- pedir aprobación;
- cortar ante errores;
- confirmar modelo real;
- ejecutar tareas pequeñas bajo prompts estrictos.

No debe hacer:

- convertirse en `queue_runner.py` distribuido;
- ejecutar código generado en host;
- ocultar fallback de modelo;
- pedir al humano operar terminal como rutina normal.

---

## Protocolo por ciclo

Cada ciclo Hermes debe iniciar con:

```text
MODEL_REAL:
PROVIDER_REAL:
CWD:
READY:
```

Luego debe ejecutar una sola unidad.

Formato mínimo:

```text
MODO: AUDIT_ONLY o WRITE_AUTHORIZED
Objetivo: una sola cosa
Archivos permitidos: solo si WRITE
Prohibido: no ampliar alcance, no commit, no push salvo orden explícita
Tests: máximo 1-2 por ciclo
Salida: VEREDICTO / EVIDENCIA / BLOQUEOS / NEXT_STEP
STOP
```

---

## Regla de no deriva

Ningún agente decide solo el cierre de un ciclo.

Todo cambio debe terminar en:

- evidencia;
- diff;
- tests o criterio equivalente;
- decisión explícita: PASS / PARTIAL / BLOCKED.

Si falta evidencia:

```text
BLOCKED_NO_EVIDENCE
```

Si el modelo real no coincide:

```text
BLOCKED_MODEL_MISMATCH
```

Si el repo no está sincronizado:

```text
BLOCKED_REPO_NOT_SYNCED
```

---

## Matriz de uso

| Trabajo | Modelo/Herramienta recomendada | Condición |
|---|---|---|
| Diseño y auditoría | Gemini 2.5 Pro | MODEL_REAL confirmado |
| Implementación corta | DeepSeek v4 Pro o Codex | TaskSpec acotado |
| Código barato/simple | Ollama/local en factory_v2 | bajo riesgo |
| Ejecución | Docker | obligatorio |
| PR/versionado | GitHub | con evidencia |
| HITL | Hermes | aprobación humana |

---

## Documentos relacionados

Canónico operativo actual:

```text
docs/factory/HERMES_RUNTIME_CANONICAL_CONFIG.md
```

Blueprint nuevo low-cost:

```text
docs/factory/BLUEPRINT_001_FACTORIA_LOW_COST_MULTIAGENTE.md
```

Blueprint industrial completo pendiente:

```text
docs/factory/BLUEPRINT_002_ARQUITECTURA_CANONICA_INDUSTRIAL.md
```

---

## Decisión final

Hermes queda gobernado por este contrato:

```text
modelo real confirmado
repo sincronizado
objetivo único
herramientas mínimas
sin escritura salvo WRITE_AUTHORIZED
salida breve
STOP explícito
```

La gobernanza anterior basada en DeepSeek v3.2 queda histórica y no debe usarse como criterio operativo actual.
