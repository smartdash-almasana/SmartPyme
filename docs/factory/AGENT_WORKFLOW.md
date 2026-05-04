# SmartPyme Factory – Protocolo Operativo de Agentes

**Versión:** 1.1  
**Capa:** FACTORY_PROTOCOL  
**Fase:** DEFINIR  
**Modelo Target:** DEEPSEEK_4_PRO  

## Decisiones de límites vigentes

### DECISIÓN 1 – Límites de iteración
- **max_iteraciones_por_fase:** 3  
- **max_intentos_correccion:** 2  

**Motivo:** Venimos de loops largos. Preferimos bloquear temprano y auditar, no consumir 90 iteraciones.

### DECISIÓN 2 – Modelos operativos autorizados
Lista canónica (no agregar otros sin autorización explícita):
- **GPT** – arquitectura, prompts, interpretación, papers, decisión de fase siguiente.
- **GEMINI** – coherencia conceptual larga, auditoría semántica, revisión de arquitectura (solo si hay tokens disponibles).
- **CODEX** – código delicado, refactor, integración con riesgo, Pydantic AI, MCP, tests complejos, pipeline/orquestadores.
- **DEEPSEEK_4_PRO** – razonamiento largo, integración compleja, fallback cuando DeepSeek 3.2 se traba, planificación operativa detallada.
- **DEEPSEEK_3_2** – auditoría corta, patch chico, contratos mínimos, verificación documental, cierre Git, tests puntuales.

**Regla:** No se pregunta qué modelo usar; se elige por dificultad y riesgo según la asignación de cada fase.

---

### DECISIÓN 3 – Modos operativos obligatorios

Toda tarea debe declarar obligatoriamente `MODO:` con uno de los siguientes valores:

- **ANALYSIS_ONLY** – solo lectura, búsqueda, inspección, diff. No escribe, no parchea, no commitea, no pushea.
- **WRITE_AUTHORIZED** – lectura + escritura permitida solo en `ARCHIVOS_PERMITIDOS`. Requiere test y cierre transaccional.
- **TEST_ONLY** – solo ejecuta tests/comandos de verificación. No modifica código fuente.
- **CLOSE_ONLY** – solo commit/push/status, sin cambiar lógica.
- **DOC_ONLY** – solo toca documentación autorizada (`.md`, `.rst`, `.txt` dentro de `docs/`).
- **BLOCKED_REVIEW** – explica bloqueo, no corrige.

**Reglas clave:**
1. **ARCHIVOS_PERMITIDOS no equivale a autorización de escritura.** Solo `WRITE_AUTHORIZED` permite escribir.
2. **FASE no define permisos.** `INTEGRAR` puede ejecutarse con `ANALYSIS_ONLY` para diseño/revisión previa.
3. **Si falta MODO → `BLOCKED_MODE_MISSING`.** No se asume modo por defecto.
4. **Si MODO no válido → `BLOCKED_MODE_INVALID`.**
5. **Si FASE y MODO se contradicen → `BLOCKED_MODE_PHASE_CONFLICT`** (ej: `INTEGRAR` + `CLOSE_ONLY`).
6. **ANALYSIS_ONLY nunca puede escribir.** Cualquier `write_file`, `patch`, `cp` activa `BLOCKED_SCOPE_VIOLATION`.

---

## Fases del workflow completo

Cada fase tiene:
- **Propósito**
- **Entrada**
- **Agente/s asignado/s**
- **Artefacto/s producidos**
- **Tests obligatorios**
- **Criterio de salida**
- **Bloqueo posible**
- **Evidencia esperada**

---

### FASE 0 – DIRECCIÓN / ORDEN DE TRABAJO
**Propósito:** Traducir la intención del arquitecto en una **TaskSpec** ejecutable.

**Entrada:**
- decisión del arquitecto;
- capa activa;
- objetivo puntual;
- restricciones.

**Agente:** GPT arquitecto.

**Salida:** TaskSpec o prompt con **CAPA, FASE, MODO, MODEL_TARGET, objetivo, archivos permitidos, prohibidos, tests y salida obligatoria**.

**Tests:** No aplica.

**Gate:** Si falta CAPA / FASE / MODO / MODEL_TARGET → `BLOCKED_LAYER_PHASE_MISSING` / `BLOCKED_MODE_MISSING` / `BLOCKED_MODEL_TARGET_MISSING`.

---

### FASE 1 – CONCEPTO
**Propósito:** Definir qué significa la capa.

**Entrada:** noción conceptual; documentos conceptuales si aplican.

**Agente:** GPT para arquitectura; Gemini si hay tokens para coherencia conceptual larga; DeepSeek 4 Pro si Gemini no está disponible.

**Salida:** definición corta:
- qué entra;
- qué sale;
- qué **no** hace;
- contratos esperados;
- límites semánticos.

**Tests:** revisión semántica, no pytest.

**Gate:** No pasa a código si no queda claro qué entra, qué sale y qué **no** hace.

---

### FASE 2 – CONTRATO DE CÓDIGO
**Propósito:** Convertir concepto en contratos mínimos.

**Entrada:** definición de capa; campos mínimos; reglas semánticas.

**Agente:** DeepSeek 3.2 para contratos simples; Codex si hay tipos delicados, validaciones complejas o compatibilidad legacy.

**Artefactos:** `app/contracts/…`, `tests/contracts/…`.

**Tecnología:**
- usar dataclass si el repo no tiene Pydantic como dependencia;
- usar Pydantic solo si ya está disponible o la TaskSpec autoriza dependencia;
- **Pydantic AI NO se usa** acá salvo que la fase sea agente/IA explícita.

**Tests:** pytest del archivo de contrato; validación de serialización; validación de errores semánticos.

**Gate:** No integrar si no hay test de contrato PASS.

---

### FASE 3 – PIEZA INTERNA / SERVICIO MÍNIMO
**Propósito:** Crear la lógica mínima que usa el contrato.

**Entrada:** contrato validado; punto funcional acotado.

**Agente:** Codex para código; DeepSeek 4 Pro si requiere razonamiento largo; DeepSeek 3.2 solo para patch chico.

**Artefactos posibles:** `app/services/…`, `app/repositories/…`, `app/catalogs/…`, `app/ai/…` solo si corresponde.

**Tests:** pytest puntual; no suite completa salvo autorización.

**Gate:** Máximo **2 archivos productivos + 1 test**, salvo TaskSpec explícita.

---

### FASE 4 – Pydantic AI / AGENTE IA
**Propósito:** Definir o ajustar agente IA cuando la capa necesita razonamiento estructurado, herramientas o salida tipada.

**Entrada:** contrato de dominio; herramienta disponible; output schema; límites de autonomía.

**Agente:** Codex si se implementa código Pydantic AI; Gemini o GPT para diseño del comportamiento; DeepSeek 4 Pro para revisar coherencia si hay mucho contexto.

**Artefactos:** `app/ai/agents/…`, `app/ai/tools/…`, `app/contracts/…` si requiere output tipado, `tests/ai/…` o `tests/contracts/…` según corresponda.

**Reglas:**
- Pydantic AI no decide negocio.
- Pydantic AI produce estructura o propuesta.
- Toda acción real pasa por DecisionRecord / AuthorizationGate.
- No llamar herramientas sin contrato explícito.
- No usar IA para reemplazar validación determinística.

**Tests:** test de output estructurado; test de herramienta mockeada; test de no ejecución sin autorización.

**Gate:** Si el agente puede ejecutar sin autorización → `BLOCKED_AUTHORIZATION_LEAK`.

---

### FASE 5 – INTEGRACIÓN
**Propósito:** Conectar la pieza al punto existente más cercano del flujo.

**Entrada:** contrato testeado; servicio/repositorio validado; punto de integración identificado.

**Agente:** Codex si toca pipeline, orquestador, MCP o persistencia crítica; DeepSeek 4 Pro si la integración es razonada pero no delicada; DeepSeek 3.2 solo si es integración muy chica.

**Reglas:**
- máximo **5 archivos leídos**;
- máximo **2 búsquedas**;
- declarar **PUNTO_DE_INTEGRACION** antes de modificar;
- máximo **2 archivos productivos**;
- máximo **1 test**.

**Tests:** test de integración puntual; no tocar todo el sistema.

**Gate:** Si no hay punto claro → `BLOCKED_INTEGRATION_POINT`.

---

### FASE 6 – MCP / HERRAMIENTA EXTERNA
**Propósito:** Exponer la capacidad al runtime Hermes solo cuando ya existe integración interna estable.

**Entrada:** servicio interno probado; contrato de herramienta; permisos claros.

**Agente:** Codex.

**Artefactos:** MCP bridge/tool si corresponde; tests MCP o tests de herramienta.

**Reglas:**
- MCP no decide.
- MCP no diagnostica.
- MCP no ejecuta acciones críticas.
- MCP expone herramientas con contratos explícitos.

**Tests:** llamada mock o test de herramienta; validación de input/output; test de rechazo si falta autorización.

**Gate:** No exponer MCP antes de integración interna PASS.

---

### FASE 7 – AUDITORÍA
**Propósito:** Verificar el patch contra la fase y la capa.

**Entrada:** diff; tests; contratos; límites.

**Agente:** DeepSeek 3.2 para auditoría corta; Gemini para coherencia conceptual larga; GPT como auditor externo si hay conflicto.

**No debe:**
- abrir arquitectura nueva;
- buscar repo completo;
- modificar archivos;
- cambiar alcance.

**Debe revisar:**
- archivos tocados;
- cumplimiento de capa;
- tests;
- violaciones semánticas;
- autorización;
- tenant_id vs cliente_id;
- pérdida de evidencia;
- diagnóstico prematuro;
- acción sin decisión.

**Salida:** PASS / PARTIAL / BLOCKED; corrección mínima si aplica.

**Gate:** No modifica archivos; no cambia alcance.

---

### FASE 8 – CORRECCIÓN MÍNIMA
**Propósito:** Resolver solo lo que la auditoría marcó.

**Agente:** Codex si es código delicado; DeepSeek 3.2 si es ajuste chico; DeepSeek 4 Pro si requiere razonamiento.

**Reglas:**
- no reabrir diseño;
- no ampliar alcance;
- solo corregir violación detectada.

**Tests:** repetir test puntual; si toca Python, ruff check si está definido por TaskSpec.

**Gate:** Si la corrección cambia arquitectura → volver a FASE 1 o `BLOCKED_SCOPE_EXPANSION`.

---

### FASE 9 – CIERRE TÉCNICO
**Propósito:** Dejar repo sincronizado y limpio.

**Agente:** DeepSeek 3.2.

**Acciones:**
- pytest puntual PASS;
- ruff si corresponde;
- git status clean o explicado;
- commit;
- push.

**Salida:** commit hash; push result; git status clean.

**Gate:** Sin push y status limpio, la fase no está cerrada.

---

### FASE 10 – PAPER / DOCUMENTACIÓN DE CIERRE
**Propósito:** Documentar lo ya construido, no inventar futuro.

**Agente:** GPT para síntesis; Gemini si hay tokens para coherencia larga; DeepSeek 3.2 para doc corto operativo.

**Artefacto:** `docs/factory` o `docs/architecture` según corresponda. **No tocar docs/product** salvo instrucción explícita.

**Debe incluir:**
- capa cerrada;
- contratos creados;
- integración realizada;
- tests;
- límites;
- riesgos pendientes;
- próxima fase.

**Gate:** Paper solo después de cierre técnico.

---

### FASE 11 – PLAN SIGUIENTE
**Propósito:** Elegir el próximo paso único.

**Agente:** GPT arquitecto.

**Salida:** siguiente TaskSpec atómica; modelo asignado; fase declarada.

**Gate:** No aplica.

---

## Reglas globales

1. **SmartPyme no decide; propone.** El dueño decide.
2. **Sin evidencia trazable no hay diagnóstico.** Sin comparación entre fuentes no hay hallazgo fuerte. Sin diferencia cuantificada no hay hallazgo accionable.
3. **No hay integración sin contrato.** No hay MCP sin integración interna. No hay paper antes del cierre.
4. **No hay acción sin DecisionRecord / AuthorizationGate.**
5. **No hardcodear semántica PyME en core.** Semántica de dominio vive en catálogos, Domain Packs o Knowledge Tanks.
6. **Cada fase tiene max_iteraciones_por_fase = 3.** Si no se alcanza criterio de salida en 3 iteraciones, bloquear y auditar.
7. **Correcciones tienen max_intentos_correccion = 2.** Si el error persiste tras 2 intentos, bloquear y escalar.

---

## Asignación de modelos por tarea

| Tarea                                    | Modelo primario   | Modelo fallback        |
|------------------------------------------|-------------------|------------------------|
| Arquitectura, prompts, decisión          | GPT               | –                      |
| Coherencia conceptual larga              | Gemini            | GPT                    |
| Código delicado, refactor, integración   | Codex             | DeepSeek 4 Pro         |
| Razonamiento largo, planificación        | DeepSeek 4 Pro    | Codex                  |
| Auditoría corta, patch chico, contratos  | DeepSeek 3.2      | DeepSeek 4 Pro         |
| Documentación de cierre                  | GPT / Gemini      | DeepSeek 3.2           |
| Cierre Git, tests puntuales              | DeepSeek 3.2      | –                      |

---

## Formato TaskSpec obligatorio

Todo prompt operativo debe declarar:

```text
CAPA:
FASE:
MODO:
MODEL_TARGET:
OBJETIVO:
ENTRADA:
ARCHIVOS_PERMITIDOS:
ARCHIVOS_SOLO_LECTURA:
PROHIBIDO:
CONTRATO_ESPERADO:
TESTS:
GATES:
SALIDA_OBLIGATORIA:
```

**MODO:** obligatorio. Valores: `ANALYSIS_ONLY`, `WRITE_AUTHORIZED`, `TEST_ONLY`, `CLOSE_ONLY`, `DOC_ONLY`, `BLOCKED_REVIEW`.

**Regla:** `ARCHIVOS_PERMITIDOS` no autoriza escritura. Solo `WRITE_AUTHORIZED` permite escribir. `FASE` no define permisos.

**Nota:** Si falta `CAPA`, `FASE`, `MODO` o `MODEL_TARGET`, responder con el bloqueo correspondiente.

---

## Bloqueos obligatorios

1. `BLOCKED_LAYER_PHASE_MISSING` – falta CAPA o FASE.
2. `BLOCKED_MODE_MISSING` – falta MODO.
3. `BLOCKED_MODE_INVALID` – MODO no autorizado.
4. `BLOCKED_MODE_PHASE_CONFLICT` – MODO contradice FASE.
5. `BLOCKED_MODEL_TARGET_MISSING` – falta MODEL_TARGET.
6. `BLOCKED_MODEL_TARGET_INVALID` – MODEL_TARGET no autorizado.
7. `BLOCKED_DIRTY_WORKTREE` – git status no clean sin justificación.
8. `BLOCKED_WRONG_BRANCH` – no está en la rama autorizada.
9. `BLOCKED_SCOPE_VIOLATION` – toca archivos no permitidos o escribe sin WRITE_AUTHORIZED.
10. `BLOCKED_CONTRACT_UNCERTAINTY` – contrato no claro o no testado.
11. `BLOCKED_INTEGRATION_POINT` – no hay punto de integración declarado.
12. `BLOCKED_AUTHORIZATION_LEAK` – agente puede ejecutar sin autorización.
13. `BLOCKED_TESTS_FAIL` – tests no pasan.
14. `BLOCKED_SCHEMA_INVALID` – esquema TaskSpec no cumple formato.

---

## Evidencia esperada por fase

Cada fase debe producir:
- **F0:** TaskSpec o prompt con campos obligatorios.
- **F1:** definición corta (texto).
- **F2:** archivo de contrato + test PASS.
- **F3:** archivo(s) de lógica + test PASS.
- **F4:** archivo de agente + test de autorización.
- **F5:** diff de integración + test PASS.
- **F6:** MCP bridge/tool + test de rechazo sin autorización.
- **F7:** informe PASS/PARTIAL/BLOCKED con corrección mínima si aplica.
- **F8:** patch correctivo + test PASS.
- **F9:** commit hash, push result, git status clean.
- **F10:** documento de cierre (`.md`).
- **F11:** siguiente TaskSpec.

---

**Última actualización:** `git rev-parse HEAD`  
**Rama:** `factory/ts-006-jobs-sovereign-persistence`  
**Estado:** Documento canónico para gobernanza operativa de SmartPyme Factory.

> **Nota:** Este protocolo debe ser referido en todos los skills operativos (`hermes_smartpyme_factory`, `smartpyme_layer_work_protocol`, etc.) y en las TaskSpecs de las fases de definición y auditoría.
