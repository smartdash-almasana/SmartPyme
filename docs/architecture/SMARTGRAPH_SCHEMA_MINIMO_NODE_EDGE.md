# SmartGraph — Schema mínimo Node/Edge

Fecha: 2026-05-09  
Estado: Diseño técnico conceptual  
Ámbito: SmartGraph / Supabase / Laboratorio PyME  
Relación: ADR-005 SmartGraph Bootstrap Strategy

---

## 1. Propósito

Este documento define el schema mínimo conceptual para iniciar SmartGraph sin contaminar el core clínico-operacional actual.

La decisión base ya aceptada es:

```text
SmartGraph nace como memoria relacional propia,
persistida en SQL/Supabase,
con modelo node/edge tipado,
y exportación graph.json.
```

Este documento no implementa migraciones todavía.
Define el contrato conceptual de persistencia.

---

## 2. Principio rector

SmartGraph debe preservar:

```text
entidades
+ relaciones
+ tenant_id
+ evidencia
+ claim_type
+ confidence
+ temporalidad
+ trazabilidad
```

Sin permitir que el LLM convierta hipótesis en hechos persistidos sin gobierno.

---

## 3. Tablas iniciales

Schema mínimo propuesto:

```text
smartgraph_nodes
smartgraph_edges
smartgraph_aliases
smartgraph_claims
```

Opcional posterior:

```text
smartgraph_exports
smartgraph_activation_logs
smartgraph_communities
```

---

## 4. smartgraph_nodes

Representa entidades canónicas o nodos operacionales/clínicos.

### Campos conceptuales

```sql
id uuid primary key

tenant_id uuid not null

node_type text not null
canonical_key text not null
label text not null
description text null

source_table text null
source_id uuid null

status text not null default 'ACTIVE'
confidence numeric null

metadata jsonb not null default '{}'

created_at timestamptz not null default now()
updated_at timestamptz not null default now()
```

### node_type esperado

```text
TENANT
EMPRESA
RECEPTION_RECORD
EVIDENCE
DOCUMENTO
CLIENTE
PROVEEDOR
PRODUCTO
FAMILIA_DE_ARTICULOS
CUENTA_BANCARIA
MOVIMIENTO
PROCESO
EVENTO
VARIABLE
FORMULA
PATOLOGIA
SINTOMA
PRACTICE
TREATMENT
MICROSERVICE
OPERATIONAL_CASE
FINDING
PREGUNTA_CLINICA
```

### Reglas

```text
tenant_id obligatorio.
canonical_key debe ser estable dentro del tenant.
node_type no debe ser texto libre sin control.
source_table/source_id vinculan con registros existentes cuando aplique.
metadata no debe reemplazar campos estructurales críticos.
```

### Constraint conceptual

```sql
unique (tenant_id, node_type, canonical_key)
```

---

## 5. smartgraph_edges

Representa relaciones tipadas entre nodos.

### Campos conceptuales

```sql
id uuid primary key

tenant_id uuid not null

from_node_id uuid not null references smartgraph_nodes(id)
to_node_id uuid not null references smartgraph_nodes(id)

edge_type text not null
claim_type text not null
confidence numeric null

valid_from timestamptz null
valid_until timestamptz null
observed_at timestamptz null

source_table text null
source_id uuid null

evidence_ids uuid[] not null default '{}'

status text not null default 'ACTIVE'
metadata jsonb not null default '{}'

created_at timestamptz not null default now()
updated_at timestamptz not null default now()
```

### edge_type esperado

Relaciones de evidencia:

```text
EXTRACTED_FROM
EVIDENCE_OF
CONFIRMADO_POR
OBSERVADO_EN
SOPORTA_HALLAZGO
```

Relaciones inferenciales:

```text
INFERIDO_DESDE
INDICATES
ACTIVA_PATOLOGIA
```

Relaciones clínicas:

```text
REQUIRES_EVIDENCE
REQUIRES_VARIABLE
SE_CALCULA_CON
SUGIERE_TRATAMIENTO
REQUIERE_REVISION_HUMANA
```

Relaciones causales/operacionales:

```text
CAUSES
AFFECTS
DEPENDS_ON
CONTRADICTS
EMPEORA
MEJORA
DERIVA_EN
```

### claim_type esperado

```text
EXTRACTED
INFERRED
AMBIGUOUS
HYPOTHESIS
VALIDATED
```

### Reglas

```text
EXTRACTED requiere evidencia directa.
INFERRED requiere confidence.
AMBIGUOUS no debe activar Finding SUPPORTED.
HYPOTHESIS no debe convertirse en hecho sin validación.
VALIDATED requiere regla determinística o revisión humana.
```

### Constraint conceptual

```sql
check (confidence is null or (confidence >= 0 and confidence <= 1))
```

---

## 6. smartgraph_aliases

Representa alias de entidades canónicas.

### Campos conceptuales

```sql
id uuid primary key

tenant_id uuid not null
node_id uuid not null references smartgraph_nodes(id)

alias text not null
alias_normalized text not null
language text null

source_table text null
source_id uuid null
confidence numeric null

status text not null default 'ACTIVE'
metadata jsonb not null default '{}'

created_at timestamptz not null default now()
updated_at timestamptz not null default now()
```

### Ejemplo

Nodo canónico:

```text
PRODUCTO_STOCK
```

Aliases:

```text
stock
mercadería
inventario
depósito
cosas
```

### Constraint conceptual

```sql
unique (tenant_id, alias_normalized, node_id)
```

---

## 7. smartgraph_claims

Representa claims explícitos cuando una afirmación necesita vida propia independiente del edge.

Uso esperado:

```text
claims clínicos
claims de ambigüedad
claims que requieren revisión humana
claims con ciclo de vida propio
```

### Campos conceptuales

```sql
id uuid primary key

tenant_id uuid not null
claim_type text not null
claim_status text not null

subject_node_id uuid null references smartgraph_nodes(id)
object_node_id uuid null references smartgraph_nodes(id)
edge_id uuid null references smartgraph_edges(id)

statement text not null
confidence numeric null

evidence_ids uuid[] not null default '{}'

requires_human_review boolean not null default false
reviewed_by text null
reviewed_at timestamptz null
review_decision text null

valid_from timestamptz null
valid_until timestamptz null
observed_at timestamptz null

metadata jsonb not null default '{}'

created_at timestamptz not null default now()
updated_at timestamptz not null default now()
```

### claim_status esperado

```text
CANDIDATE
ACTIVE
SUPPORTED
REJECTED
DEPRECATED
BLOCKED
```

### Regla crítica

```text
Un claim INFERRED/HYPOTHESIS no puede pasar a SUPPORTED sin evidencia suficiente,
validación determinística o revisión humana.
```

---

## 8. Ejemplo completo

Entrada del dueño:

```text
vendo mucho pero no queda plata
```

### Nodo síntoma

```text
node_type: SINTOMA
canonical_key: vendo_mucho_no_queda_plata
label: Vendo mucho pero no queda plata
```

### Nodo patología

```text
node_type: PATOLOGIA
canonical_key: margen_erosionado
label: Margen erosionado
```

### Edge inferencial

```text
from: vendo_mucho_no_queda_plata
to: margen_erosionado
edge_type: INDICATES
claim_type: HYPOTHESIS
confidence: 0.62
```

### Nodo fórmula

```text
node_type: FORMULA
canonical_key: margen_bruto
label: Margen bruto
```

### Edge clínico

```text
from: margen_erosionado
to: margen_bruto
edge_type: REQUIRES_VARIABLE
claim_type: VALIDATED
confidence: 1.0
```

### Nodo evidencia requerida

```text
node_type: EVIDENCE
canonical_key: ventas_periodo
label: Ventas del período
```

### Edge requerido

```text
from: margen_erosionado
to: ventas_periodo
edge_type: REQUIRES_EVIDENCE
claim_type: VALIDATED
confidence: 1.0
```

---

## 9. Relación con contratos existentes

SmartGraph no reemplaza los contratos clínico-operacionales existentes.

Debe poder vincularse con ellos usando:

```text
source_table
source_id
```

Ejemplos:

```text
ReceptionRecord → smartgraph_nodes
EvidenceRecord → smartgraph_nodes
PathologyCandidate → smartgraph_claims
FormulaExecution → smartgraph_nodes / smartgraph_edges
OperationalCase → smartgraph_nodes
FindingRecord → smartgraph_nodes / smartgraph_claims
```

---

## 10. Reglas de escritura

### Escritura permitida

```text
servicios determinísticos
repositorios controlados
migraciones revisadas
procesos con tenant_id
```

### Escritura no permitida

```text
LLM directo a tablas SmartGraph
prompts libres creando memoria soberana
claims inferidos marcados como SUPPORTED sin control
edges sin tenant_id
edges sin claim_type
```

---

## 11. Export graph.json

El schema debe permitir exportar:

```json
{
  "tenant_id": "...",
  "nodes": [],
  "edges": [],
  "claims": [],
  "aliases": []
}
```

Uso esperado:

- visualización;
- spike Graphify;
- clustering;
- análisis topológico;
- debug;
- auditoría.

El export no es la fuente soberana.

```text
La fuente soberana sigue siendo SQL/Supabase.
```

---

## 12. Fases sugeridas

### Fase 1 — Schema conceptual

```text
documentar tablas y reglas
```

### Fase 2 — Migración mínima

```text
crear tablas node/edge/alias/claim
```

### Fase 3 — Repositorio SmartGraph mínimo

```text
create_node
create_edge
add_alias
create_claim
export_graph_json
```

### Fase 4 — Spike local

```text
crear nodos desde datos ya existentes
sin tocar flujo clínico principal
```

### Fase 5 — Activación contextual

```text
síntoma → subgrafo relevante
```

---

## 13. Límites explícitos

Este schema no autoriza todavía:

```text
- clustering automático en producción
- persistencia autónoma de inferencias LLM
- modificación del motor clínico
- reemplazo de Supabase
- adopción de Neo4j
- adopción productiva de Graphify
```

---

## 14. Frase rectora

```text
SmartGraph empieza pequeño:
nodos, relaciones, evidencia y tiempo.
```

---

## 15. Cierre

Este schema mínimo permite iniciar SmartGraph como memoria estructural propia sin romper lo ya cerrado.

El objetivo no es agregar complejidad.

El objetivo es preparar una capa donde cada hallazgo, patología, fórmula, evidencia y síntoma pueda quedar conectado de forma trazable, temporal y activable.
