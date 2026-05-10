# SmartPyme — Agent Harness Governance V1

## Objetivo

Unificar el comportamiento operativo de:

- GPT / ChatGPT
- Codex
- Kiro
- futuros agentes multiagente
- skills
- specs
- steering files
- prompts
- ADRs
- docs
- runtime governance

bajo un mismo modelo de harness operacional.

---

# 1. PRINCIPIO RECTOR

SmartPyme NO es:

- un chatbot;
- un wrapper de LLM;
- una colección de prompts;
- una automatización genérica.

SmartPyme ES:

```text
Evidence Operating System
+
Harness Engineering
+
Operational Memory
+
Tenant Isolation
+
Governed Agent Orchestration
```

Regla:

```text
harness > agentes
contratos > prompts
evidencia > intuición
rollback > autonomía ciega
microciclos > reescrituras masivas
```

---

# 2. PROMPT HARNESS STANDARD

Todos los prompts importantes deben seguir esta estructura.

## FASE 0 — AUDITORÍA PREVIA

Validar:

- rama git;
- archivos presentes;
- scope;
- constraints;
- riesgos;
- contexto faltante.

Si el contexto es insuficiente:

```text
BLOCKED
```

No ejecutar.

---

## FASE 1 — IDENTIDAD Y CONTEXTO

Definir:

- rol metodológico;
- constraints;
- archivos permitidos;
- archivos prohibidos;
- objetivo exacto;
- criterios de aceptación.

Nunca usar títulos vacíos tipo:

```text
Senior AI Engineer
```

Usar:

```text
ReAct
HITL
DAGs
pgvector
event-driven
contracts
```

---

## FASE 2 — PANEL DIVERGENTE

Toda decisión importante debe considerar:

```text
negocio
riesgo
adopción
```

Panel recomendado:

- CFO real;
- adversarial reviewer;
- operador no técnico.

---

## FASE 3 — ENTREGA CON KPIs

Toda arquitectura debe declarar:

- latencia;
- costo;
- tasa HITL;
- fallback;
- rollback;
- límites.

Nunca:

```text
"la IA ayudará"
"de manera eficiente"
```

---

## FASE 4 — RESTRICCIONES

Definir explícitamente:

- archivos prohibidos;
- frameworks prohibidos;
- runtime prohibido;
- wiring prohibido;
- límites del patch.

---

## FASE 5 — REFINAMIENTO SEPARADO

La crítica NO ocurre en el mismo turno.

Separar:

```text
V1 = diseño
V2 = debug/autocrítica
```

---

# 3. ROLES DE AGENTES

## GPT / ChatGPT

Responsable de:

- síntesis;
- arquitectura;
- tradeoffs;
- handoffs;
- gobernanza;
- extracción de estándares;
- diseño de microciclos.

NO debe:

- asumir estado de repo sin evidencia;
- afirmar tests no ejecutados;
- inventar runtime.

---

## KIRO

Responsable de:

- specs;
- requirements;
- design docs;
- tasks;
- steering;
- migration plans;
- acceptance criteria;
- consumer contracts.

Kiro NO debe:

- hacer rewrites masivos;
- tocar runtime sin permiso explícito;
- alterar pipeline productivo.

---

## CODEX

Responsable de:

- implementación pequeña;
- bugfixes;
- repairs;
- compatibilidad legacy;
- tests;
- validación.

Codex NO debe:

- inventar arquitectura;
- expandir scope;
- mezclar docs + runtime + DB + wiring.

---

# 4. ESTÁNDAR DE BRANCHES

Antes de cualquier tarea:

```bash
git branch --show-current
git status --short
git log --oneline -5
```

Branch productiva actual esperada:

```text
product/laboratorio-mvp-vendible
```

Si la rama es incorrecta:

```text
BLOCKED
```

---

# 5. SMARTGRAPH STANDARD

SmartGraph es:

```text
memoria estructural gobernada
```

NO:

```text
memoria autónoma libre
```

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
human review
```

Prohibido:

```text
LLM direct writes
cross-tenant access
activation engine prematuro
claims inferidos → supported automáticos
```

---

# 6. LEGACY COMPATIBILITY STANDARD

Nunca romper contratos legacy sin auditoría.

Patrón obligatorio:

```text
legacy estable
+
nuevo servicio separado
+
tests separados
+
migración posterior
```

Ejemplo:

```text
EntityResolutionService
SmartGraphEntityResolutionService
```

---

# 7. CONSUMER CONTRACT ENFORCEMENT

Los servicios SmartGraph deben consumir:

```text
input contracts explícitos
```

NO kwargs sueltos.

Patrón:

```python
entity_input = build_entity_resolution_input(...)
service.resolve_or_create_entity(entity_input)
```

Objetivo:

```text
validación centralizada
immutability
anti-deriva
anti-bypass
```

---

# 8. OUTPUT STANDARD

Todos los agentes deben responder:

```text
VEREDICTO:
CAMBIOS_REALIZADOS:
TESTS:
RIESGOS:
BUGS_REMANENTES:
PROXIMO_MICROCICLO:
```

Auditorías:

```text
HALLAZGOS:
EVIDENCIA:
DECISION_RECOMENDADA:
```

---

# 9. ANTI-PATTERNS

Nunca:

- rewrites gigantes;
- mezclar 8 capas en un patch;
- usar prompts como reemplazo de arquitectura;
- tocar wiring antes de auditoría;
- integrar activation engine prematuramente;
- meter frameworks por moda;
- asumir contexto inexistente.

---

# 10. SAFE SEQUENCE ACTUAL

```text
repository layer
→ docs/ADR/schema
→ entity resolution
→ integration contract
→ consumer contract enforcement
→ wiring controlado
→ activation engine
→ RLS/hardening
```

---

# 11. ARCHIVOS RECOMENDADOS

## Root

```text
AGENTS.md
```

## Kiro

```text
.kiro/steering/
.kiro/specs/
```

## Arquitectura

```text
docs/adr/
docs/architecture/
docs/database/
docs/operations/
```

---

# 12. SKILLS RECOMENDADAS

## skill: branch_guard

Valida:

- branch;
- dirty tree;
- últimos commits.

---

## skill: scope_guard

Valida:

- archivos permitidos;
- archivos prohibidos.

---

## skill: legacy_audit

Busca:

- imports;
- consumidores;
- contratos legacy.

---

## skill: smartgraph_contract_check

Valida:

- tenant isolation;
- claim_type;
- confidence;
- human review.

---

## skill: prompt_harness_check

Evalúa:

- Fase 0;
- constraints;
- KPIs;
- panel divergente;
- refinamiento separado.

---

# 13. DIRECCIÓN ESTRATÉGICA

SmartPyme no debe derivar hacia:

```text
"agentes autónomos mágicos"
```

Debe evolucionar hacia:

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

---

# 14. REGLA FINAL

Cuando exista duda:

```text
detener
verificar
reducir sco