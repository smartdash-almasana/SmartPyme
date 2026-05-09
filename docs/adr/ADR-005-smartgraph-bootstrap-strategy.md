# ADR-005 — SmartGraph Bootstrap Strategy

Fecha: 2026-05-09  
Estado: Aceptado  
Ámbito: SmartGraph / SmartPyme / Laboratorio PyME

---

## 1. Contexto

SmartPyme incorporó SmartGraph como capa conceptual de memoria estructural persistente.

Ya existen:

- contratos clínico-operacionales;
- repositorios;
- motor clínico;
- hallazgos;
- Harness Engineering;
- persistencia SQL/Supabase.

La necesidad ahora es decidir:

```text
cómo nace SmartGraph técnicamente
sin contaminar el core actual.
```

---

## 2. Problema

Existen varias alternativas posibles:

```text
A. módulo interno propio
B. wrapper directo de Graphify
C. tablas relacionales node/edge
D. motor de grafos dedicado
E. híbrido SQL + export graph.json
```

El riesgo principal es:

```text
introducir complejidad arquitectónica prematura.
```

SmartPyme todavía necesita:

- estabilidad clínica;
- soberanía determinística;
- evolución incremental;
- trazabilidad;
- aislamiento por tenant;
- persistencia gobernada.

---

## 3. Decisión

SmartGraph nace inicialmente como:

```text
módulo interno relacional
persistido en SQL/Supabase
con modelo node/edge tipado
más exportación graph.json.
```

La estrategia formal es:

```text
C. tablas relacionales edge/node
+
E. export graph.json
```

---

## 4. Decisiones explícitas

### Sí se acepta

```text
- node tables
- edge tables
- claim_type
- confidence
- tenant_id
- temporalidad
- canonical entities
- aliases
- export graph.json
- activación contextual
- incremental updates
```

### No se acepta todavía

```text
- reemplazar Supabase
- introducir Neo4j de entrada
- introducir Graphify como runtime productivo
- permitir escritura directa del LLM
- mezclar memoria experimental con core clínico
- rediseñar contratos ya cerrados
```

---

## 5. Razones

### 5.1 Compatibilidad con arquitectura actual

La arquitectura actual ya está basada en:

```text
Pydantic
+ contratos
+ repositorios
+ Supabase
+ determinismo operacional
```

Un modelo relacional node/edge encaja naturalmente.

---

### 5.2 Soberanía operacional

SQL/Supabase preserva:

- control transaccional;
- auditoría;
- trazabilidad;
- multi-tenant;
- versionado;
- gobierno determinístico.

---

### 5.3 Evolución incremental

La decisión evita:

```text
big bang arquitectónico
```

Y permite:

```text
agregar capacidades gradualmente
```

Ejemplo:

```text
node/edge
→ export graph.json
→ clustering
→ activación contextual
→ visualización
→ análisis topológico avanzado
```

---

### 5.4 Separación entre producto y experimento

Graphify puede inspirar o analizar exports.

Pero:

```text
la memoria soberana no depende de Graphify.
```

Esto evita:

- lock-in conceptual;
- acoplamiento externo;
- contaminación del runtime productivo.

---

## 6. Modelo mental oficial

SmartGraph no nace como “base de grafos”.

Nace como:

```text
memoria relacional empresarial
exportable a representación de grafo.
```

Frase rectora:

```text
SQL persiste.
SmartGraph estructura.
LLM interpreta.
Harness gobierna.
```

---

## 7. Arquitectura inicial esperada

Conceptualmente:

```text
Evidence
→ entidades
→ relaciones
→ activación contextual
→ motor clínico
→ hallazgos
```

Persistencia inicial:

```text
smartgraph_nodes
smartgraph_edges
smartgraph_aliases
smartgraph_claims
```

Exportaciones:

```text
graph.json
subgraph.json
activation_context.json
```

---

## 8. Rol de Graphify

Graphify queda reinterpretado como:

```text
fuente de inspiración conceptual
```

Y eventualmente:

```text
herramienta experimental/spike sobre exports
```

No como:

```text
runtime soberano del sistema.
```

---

## 9. Límites explícitos

Este ADR no autoriza todavía:

```text
- implementación productiva completa
- clustering automático
- inferencia autónoma persistente
- graph analytics complejos
- autoescritura de memoria por LLM
- adopción de motor de grafos externo
```

---

## 10. Próximo paso permitido

El siguiente paso válido después de este ADR es:

```text
diseñar schema conceptual mínimo node/edge
```

Sin tocar todavía:

- motor clínico;
- flujo de hallazgos;
- contratos cerrados;
- runtime principal.

---

## 11. Cierre

Esta decisión preserva:

```text
simplicidad operacional
+
soberanía determinística
+
evolución incremental
```

Y evita transformar SmartPyme en:

```text
experimento multiagente descontrolado.
```

SmartGraph se incorpora como:

```text
capa estructural de memoria empresarial
```

sin romper:

- el core actual;
- la estabilidad clínica;
- la arquitectura basada en contratos.
