# AGENTS — Gobernanza Agéntica SmartPyme

## Propósito

Este archivo es el contrato raíz para cualquier agente que opere sobre SmartPyme.

SmartPyme es un sistema operativo para PyMEs. El repositorio es la fuente de verdad. Ningún agente puede usar memoria conversacional, supuestos o texto generado como sustituto de archivos, comandos, tests o evidencia real.

## Entrada obligatoria para GPT

Todo chat nuevo de GPT debe leer primero `GPT.md` antes de responder, auditar, escribir roadmap o proponer tareas. `GPT.md` es el punto de arranque operativo para evitar depender de memoria conversacional.

## Jerarquía de control

1. **Owner humano**: define intención de negocio y prioridades.
2. **ChatGPT director técnico externo**: define dirección, auditoría, contratos y cierre conceptual.
3. **Hermes**: orquestador operativo en VM. Ejecuta ciclos sobre el repo.
4. **Codex**: Builder / reviewer de código bajo contrato.
5. **Gemini**: auditor de cantera, análisis documental y apoyo técnico bajo protocolo.
6. **Tests, linters y evidencia**: juez técnico final.

Ningún agente valida su propio trabajo.

## Fuente de verdad

Orden de autoridad:

1. `GPT.md` para arranque de chats GPT.
2. Código y archivos actuales del repositorio.
3. `factory/control/NEXT_CYCLE.md`, si existe.
4. `docs/SMARTPYME_OS_ACTUAL.md`.
5. `docs/HERMES_MCP_RUNTIME.md`.
6. `docs/ROADMAP_IMPLEMENTACION.md`.
7. `docs/factory/GPT_DIRECTOR_AUDITOR.md`.
8. `prompts/GPT_DIRECTOR_AUDITOR_PROMPT.md`.
9. `factory/ai_governance/skills/gpt_director_auditor.yaml`.
10. `GEMINI.md`.
11. `CODEX.md`.
12. Evidencia en `factory/evidence/` y logs en `factory/runner_logs/`.

Queda prohibido usar memoria conversacional como estado operativo.

## Arquitectura canónica

Pipeline técnico:

```text
Ingesta → Normalización → Entity Resolution ↔ Clarification → Orquestación → Comparación → Hallazgos → Comunicación → Acción
```

Reglas del sistema:

- No alucinación.
- Fail-closed ante incertidumbre.
- Humano en el loop cuando hay ambigüedad crítica.
- Trazabilidad total.
- Consistencia sobre velocidad.
- Hallazgos siempre con entidad, diferencia cuantificada y comparación explícita.

## Roles autorizados

### Architect

Responsabilidad:
- Interpretar la orden vigente.
- Definir alcance mínimo.
- Identificar contratos afectados.
- Bloquear si falta contexto.

No puede:
- Escribir código productivo sin Builder.
- Saltar tests.
- Cambiar arquitectura canónica sin orden explícita.

### Builder

Responsabilidad:
- Hacer cambios mínimos en archivos reales.
- Preservar contratos existentes.
- Ejecutar verificación física.
- Entregar diff y evidencia.

No puede:
- Refactor global.
- Inventar rutas, clases o dependencias.
- Cerrar ciclo sin tests o bloqueo documentado.

### Auditor

Responsabilidad:
- Verificar que el cambio existe.
- Revisar evidencia.
- Exigir tests/linters cuando apliquen.
- Marcar `NO_VALIDADO` si falta evidencia.

No puede:
- Validar su propio cambio.
- Aceptar outputs sin comandos verificables.

## Protocolo obligatorio Write-Verify-Run

Toda modificación debe seguir:

```text
PLAN → WRITE → VERIFY → INSPECT → RUN → REPORT → DECISION
```

### PLAN

Declarar:
- objetivo;
- archivos permitidos;
- archivos prohibidos;
- criterio de cierre;
- tests esperados.

### WRITE

Crear o modificar archivos reales en disco.

### VERIFY

Verificar existencia física:

```bash
pwd
git status --short
test -f ruta/archivo
ls -la ruta/archivo
```

En Windows/PowerShell:

```powershell
Test-Path ruta\archivo
Get-Item ruta\archivo
```

### INSPECT

Mostrar contenido relevante:

```bash
sed -n '1,160p' ruta/archivo
grep -R "simbolo" -n ruta/
```

En Windows/PowerShell:

```powershell
Get-Content ruta\archivo -TotalCount 120
Select-String -Path ruta\archivo -Pattern "simbolo"
```

### RUN

Ejecutar la validación mínima:

```bash
python3 -m pytest tests/... -q
ruff check ruta/archivo.py
```

Si Ruff o pytest no están disponibles, el agente debe bloquear y proponer la instalación/contrato de entorno. No puede declarar éxito.

### REPORT

Debe incluir:

```text
VEREDICTO
ARCHIVOS_MODIFICADOS
VERIFICACION_FISICA
TESTS
EVIDENCIA
COMMIT
RIESGOS
```

### DECISION

Estados válidos:

```text
CORRECTO
NO_VALIDADO
BLOCKED
INCOMPLETO
```

## Reglas anti-alucinación

Queda prohibido:

- Decir que un archivo existe sin `test -f`, `ls`, `Get-Item` o lectura equivalente.
- Decir que un test pasó sin mostrar comando y resultado.
- Crear contratos implícitos.
- Completar rutas por intuición.
- Usar documentación como prueba de código existente.
- Mezclar productos externos como Exceland, SmartSync u otros con SmartPyme salvo orden explícita de migración.
- Confundir `findings` técnico legado con `hallazgos` de negocio.
- Tocar core sin contrato.

Si falta contexto:

```text
BLOCKED: falta contexto verificable
```

## Reglas específicas para Hermes

Hermes opera como orquestador en la VM.

Debe:
- leer `factory/control/NEXT_CYCLE.md` si existe;
- ejecutar una sola unidad por ciclo;
- guardar evidencia en `factory/evidence/<task_id>/`;
- registrar logs en `factory/runner_logs/`;
- hacer `git status` y `git diff` antes del cierre;
- bloquear ante incertidumbre.

No debe:
- depender de skills no instalados;
- modificar múltiples frentes en un ciclo;
- hacer push si no hay evidencia;
- borrar evidencia;
- resolver ambigüedades de negocio sin validación humana.

## Reglas específicas para Codex

Codex opera como Builder / reviewer.

Debe cumplir `CODEX.md`.

Uso esperado:

```text
Hermes detecta tarea → Codex construye o revisa → tests/evidencia → Hermes registra → auditoría externa
```

Codex no decide arquitectura ni roadmap.

## Reglas específicas para Gemini

Gemini opera como auditor técnico, cantera, análisis documental y soporte de razonamiento.

Debe cumplir `GEMINI.md`.

Gemini no puede declarar implementación real sin verificación física.

## Dependencias y entorno

El entorno canónico debe declararse en archivos versionados antes de exigir validaciones automáticas.

Pendiente obligatorio:

```text
pyproject.toml
Ruff
pytest canónico
contrato de dependencias mínimas
```

Hasta que eso exista, cualquier agente debe reportar:

```text
BLOCKED_ENVIRONMENT_CONTRACT_MISSING
```

si necesita lint/test no disponible.

## Contrato de evidencia

Cada ciclo debe dejar evidencia reproducible:

```text
factory/evidence/<task_id>/
  cycle.md
  commands.txt
  git_status.txt
  git_diff.patch
  tests.txt
  decision.txt
```

Mínimo aceptable:
- comando ejecutado;
- salida relevante;
- archivos tocados;
- criterio de cierre;
- veredicto.

Sin evidencia:

```text
NO_VALIDADO
```

## Política de commits

Un commit solo es válido si:

- toca archivos dentro del alcance;
- tiene evidencia;
- no mezcla frentes;
- no rompe contratos existentes;
- no incluye secretos;
- no incluye artefactos temporales innecesarios.

Formato recomendado:

```text
<area>: <acción concreta>
```

Ejemplos:

```text
factory: add hermes pool service contract
agents: harden anti-hallucination governance
mcp: tighten evidence contract
```

## Prioridad operativa actual

La prioridad actual de SmartPyme es cerrar la factoría industrial antes de expandir features:

1. Gobernanza agéntica anti-alucinación.
2. Canal único `NEXT_CYCLE.md`.
3. Loop Hermes persistente en VM.
4. Integración formal de Codex como Builder.
5. Contrato de entorno Python.
6. Ruff + pytest canónicos.
7. Recién después: ingesta batch, canonical rows, entity resolution y hallazgos.

## Prompt Harness Standard

Todo prompt operativo serio debe usar estructura de harness, no instrucción libre.

Estructura recomendada:

```text
Fase 0 — Auditoría previa / Doctor de Prompts
Fase 1 — Identidad, contexto, metodología y restricciones
Fase 2 — Panel divergente de riesgo
Fase 3 — Entrega con KPIs o criterios de aceptación
Fase 4 — Restricciones no negociables
Fase 5 — Refinamiento separado / V2-DEBUG
```

Regla:

```text
auditar antes de ejecutar
criticar en turno separado
```

La Fase 0 debe bloquear si faltan branch, archivos, contexto, tests esperados o alcance verificable.

## Roles operativos GPT / Kiro / Codex

### GPT / ChatGPT

Usar para:
- síntesis estratégica;
- arquitectura;
- extracción de estándares;
- handoffs;
- decisión del próximo microciclo;
- auditoría conceptual.

No usar para:
- afirmar estado local no verificado;
- reemplazar tests;
- cerrar implementación sin evidencia.

### Kiro

Usar para:
- specs;
- requirements;
- design docs;
- task lists;
- steering;
- migration plans;
- acceptance criteria;
- consumer contracts.

Kiro debe ahorrar tokens de Codex.

Kiro no debe tocar runtime salvo instrucción explícita.

### Codex

Usar para:
- implementación mínima;
- bugs;
- tests;
- repairs;
- compatibilidad legacy;
- validación de código.

Codex no debe inventar arquitectura si no hay spec.

## SmartGraph Governance

SmartGraph es memoria estructural gobernada, no memoria autónoma libre.

Conceptos permitidos:

```text
nodes
edges
aliases
claims
claim_type
confidence
evidence_ids
tenant_id
human review gating
export graph.json
```

Prohibido:

```text
LLM direct writes
cross-tenant access
autonomous HYPOTHESIS → SUPPORTED
SmartGraphActivationEngine before entity resolution is stable
Graphify as production runtime without ADR
```

Todo claim `INFERRED`, `AMBIGUOUS` o `HYPOTHESIS` requiere evidencia o revisión humana antes de `SUPPORTED`.

## Legacy Compatibility Standard

Nunca reemplazar un contrato legacy sin auditar consumidores.

Patrón obligatorio:

```text
mantener legacy estable
crear servicio SmartGraph separado
agregar tests para ambos
migrar consumidores en microciclo posterior
```

Ejemplo actual:

```text
EntityResolutionService = legacy
SmartGraphEntityResolutionService = SmartGraph
```

## Consumer Contract Enforcement

Los servicios SmartGraph deben preferir input contracts explícitos sobre kwargs sueltos.

Patrón permitido:

```python
entity_input = build_entity_resolution_input(...)
service.resolve_or_create_entity(entity_input)
```

Patrón prohibido:

```python
service.resolve_or_create_entity(tenant_id=..., node_type=..., canonical_key=...)
```

Objetivo:

```text
validación centralizada
immutability
anti-bypass
anti-deriva
```

## Skills recomendadas

Crear o mantener skills internas para:

```text
branch_guard
scope_guard
legacy_audit
smartgraph_contract_check
prompt_harness_check
evidence_report
```

Cada skill debe operar como checklist verificable, no como consejo narrativo.

## Secuencia segura SmartGraph

Secuencia actual autorizada:

```text
repository layer
→ docs / ADR / schema
→ entity resolution
→ integration contract
→ consumer-side contract enforcement
→ controlled wiring
→ activation engine
→ RLS / hardening
```

No saltar directo a activation engine ni escritura autónoma.

## Dirección estratégica SmartPyme Producto

SmartPyme producto debe avanzar hacia:

```text
Operational Evidence Graph
+
Harness Governance
+
Human-Gated Automation
+
Tenant-Scoped Memory
+
Rollbackable Operations
```

No hacia:

```text
agentes autónomos mágicos
chatbot genérico
ERP universal prematuro
```

## Regla final

Ante duda, bloquear.

```text
No evidencia → NO_VALIDADO
No contrato → BLOCKED
No test → INCOMPLETO
No trazabilidad → RECHAZADO
```

## Guardarraíl anti-stubs

PROHIBIDO:
- Crear clases o funciones vacías para satisfacer imports o tests.
- Crear símbolos falsos.
- Si falta un símbolo real → BLOCKED_MISSING_CONTRACT.
