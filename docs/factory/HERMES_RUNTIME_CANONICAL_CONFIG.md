# HERMES_RUNTIME_CANONICAL_CONFIG

Estado: CANONICO v1  
Fecha: 2026-05-06  
Alcance: SmartPyme Factory / Hermes Gateway / uso operativo con agentes

---

## VEREDICTO

Hermes debe operar como gateway disciplinado de SmartPyme Factory, no como agente autónomo ilimitado.

La configuración runtime debe privilegiar:

- modelo real confirmado;
- ejecución corta;
- pocas herramientas por ciclo;
- no lectura innecesaria de memoria/sesiones;
- no modificación de repo sin modo WRITE explícito;
- salida breve;
- corte rápido si el modelo, provider o contexto no coinciden.

---

## ESTADO OBJETIVO

Hermes debe iniciar cada ciclo operativo confirmando:

```text
MODEL_REAL:
PROVIDER_REAL:
CWD:
READY:
```

Si `MODEL_REAL` no coincide con el modelo pedido, el ciclo no es válido para WRITE.

---

## MODELO ACTUAL OBJETIVO

Para esta etapa de diseño/freeze:

```text
MODEL_REAL: google/gemini-2.5-pro
PROVIDER_REAL: gemini
```

Uso permitido:

- auditoría;
- diseño;
- comparación documental;
- revisión de blueprint;
- tareas de lectura controlada.

Uso no permitido:

- implementación larga;
- refactor amplio;
- tocar repo sin autorización;
- arreglar tests por intuición;
- iterar hasta agotar turnos.

---

## RUTA OPERATIVA ESPERADA

```text
CWD: /opt/smartpyme-factory/repos/SmartPyme
BRANCH_BASE: factory/ts-006-jobs-sovereign-persistence
BASELINE_SANO: 86237e4 / HITO_009
```

Antes de auditar archivos del repo, Hermes debe estar sincronizado:

```bash
git fetch origin
git checkout factory/ts-006-jobs-sovereign-persistence
git pull --ff-only
```

Si no se sincroniza, sus conclusiones sobre existencia de archivos no son confiables.

---

## CONFIG LOCAL OBSERVADA

Config local leída en VM:

```text
/home/neoalmasana/.hermes/config.yaml
```

Valores relevantes observados:

```text
model.default: google/gemini-2.5-pro
model.provider: google/gemini
terminal.cwd: /opt/smartpyme-factory/repos/SmartPyme
terminal.backend: local
checkpoints.enabled: true
```

Riesgos observados en configuración previa:

```text
max_turns demasiado alto
gateway_timeout demasiado largo
tool_use_enforcement auto
skills/session_search/clarify activables sin necesidad
streaming inicialmente desactivado
```

Valores recomendados para operación disciplinada:

```yaml
agent:
  max_turns: 18
  gateway_timeout: 600
  api_max_retries: 1
  gateway_timeout_warning: 180
  gateway_notify_interval: 60

display:
  streaming: true
  interim_assistant_messages: false
```

---

## SKILLS

La fuente versionada de skills SmartPyme debe ser:

```text
/opt/smartpyme-factory/repos/SmartPyme/factory/ai_governance/skills
```

No se deben editar skills directamente en:

```text
~/.hermes/skills/
```

Si Hermes usa `skills.search_paths`, debe apuntar al directorio versionado del repo.

Si la versión instalada usa `skills.external_dirs`, debe apuntar al mismo directorio.

No asumir la clave correcta sin verificarla contra la versión real de Hermes instalada.

Criterio de verificación:

```text
Hermes debe listar o reconocer hermes_smartpyme_factory desde el directorio versionado del repo.
```

Si no puede verificarse:

```text
BLOCKED_HERMES_SKILLS_NOT_VERIFIED
```

---

## MCP

El template versionado declara MCP SmartPyme por stdio contra:

```text
/opt/smartpyme-factory/repos/SmartPyme/mcp_smartpyme_bridge.py
```

Pero el estado operativo observado históricamente fue:

```text
MCP configurado != herramientas MCP cargadas en runtime
```

Por lo tanto:

- MCP no debe considerarse activo hasta verificar tools registradas.
- No usar NotebookLM/MCP para tareas críticas hasta cierre de auditoría MCP.
- No exponer tools de escritura cloud sin allowlist e HITL.

Si no hay tools MCP reales:

```text
BLOCKED_HERMES_MCP_REGISTRY
```

---

## DOCUMENTOS HISTÓRICOS / DRIFT

Este documento reemplaza como referencia operativa actual a documentos que mencionan DeepSeek v3.2 como primario.

Documentos históricos útiles pero no canónicos para la etapa actual:

```text
docs/factory/HERMES_CODEX_GEMINI_GOVERNANCE.md
```

Ese documento describe una etapa anterior donde DeepSeek v3.2 era primario y Gemini era objetivo/fallback. Para la etapa actual, Hermes ya debe confirmar `google/gemini-2.5-pro` como `MODEL_REAL` antes de trabajar.

---

## PROTOCOLO DE PROMPTS PARA HERMES

Hermes debe recibir prompts pequeños.

Formato AUDIT:

```text
MODO: AUDIT_ONLY

Objetivo:
[una sola cosa]

No modificar archivos.
No commit.
No push.
No usar session_search.
No usar skills_list.
No pedir aclaración.
No ampliar alcance.

Ejecutá solo:
[1 o 2 comandos]

Salida:
VEREDICTO:
EVIDENCIA:
RIESGO:
NEXT_STEP:

STOP.
```

Formato WRITE:

```text
MODO: WRITE_AUTHORIZED

Objetivo:
[un cambio mínimo]

Archivos permitidos:
- archivo_1
- archivo_2

Prohibido:
- no tocar app/**
- no tocar config
- no commit
- no push
- no ampliar alcance
- no usar session_search
- no usar skills_list

Tests:
[1 o 2 tests máximo]

Salida:
VEREDICTO:
ARCHIVOS_MODIFICADOS:
TEST_RESULT:
BLOQUEOS:
NEXT_STEP:

STOP.
```

---

## PROMPTS PROHIBIDOS

No enviar a Hermes prompts del tipo:

```text
investigá todo
seguí hasta cerrar
arreglá todos los tests
diseñá toda la arquitectura e implementala
continuá sin frenar
```

Estos prompts provocan:

- loops largos;
- gasto de tokens;
- lectura excesiva;
- mezclas de alcance;
- modificación accidental de capas viejas.

---

## USO CORRECTO EN LA NUEVA ETAPA

Hermes no debe operar como centro de la factoría.

Rol correcto:

```text
Hermes = gateway humano + HITL + operador disciplinado de tareas pequeñas
```

No debe reemplazar:

```text
LangGraph = orquestación multiagente
Docker = ejecución segura
GitHub = PR y versionado
Pydantic = contratos
```

---

## CHECKLIST ANTES DE CADA CICLO

1. Confirmar `MODEL_REAL`.
2. Confirmar `PROVIDER_REAL`.
3. Confirmar `CWD`.
4. Confirmar rama.
5. Confirmar que el repo está sincronizado si se va a leer documentación reciente.
6. Confirmar modo: AUDIT_ONLY o WRITE_AUTHORIZED.
7. Confirmar máximo 1 objetivo.
8. Confirmar STOP al final.

---

## DECISIÓN FINAL

Para SmartPyme Factory, Hermes queda operativo solo bajo este contrato:

```text
modelo confirmado
repo sincronizado
objetivo único
herramientas mínimas
salida breve
sin escritura salvo WRITE_AUTHORIZED
STOP explícito
```

Cualquier ejecución fuera de este contrato debe considerarse no confiable para cerrar hitos o modificar arquitectura.
