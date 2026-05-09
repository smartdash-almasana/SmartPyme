# SmartGraph — Ontología y Relaciones

Fecha: 2026-05-09  
Estado: Arquitectura conceptual  
Ámbito: SmartGraph / SmartPyme / Laboratorio PyME  
Relación: SMARTPYME_SMARTGRAPH_ARQUITECTURA_CONCEPTUAL.md

---

## 1. Propósito

Este documento define la ontología conceptual inicial de SmartGraph.

SmartGraph necesita:

```text
entidades
+ relaciones
+ temporalidad
+ evidencia
+ confidence
+ activación contextual
```

No es solamente un esquema de datos.
Es el modelo semántico-operacional de la memoria empresarial de SmartPyme.

---

## 2. Principio rector

SmartGraph separa explícitamente:

```text
hechos observados
≠
inferencias
≠
hipótesis
≠
verdad validada
```

Toda relación debe conservar:

- origen;
- evidencia;
- confidence;
- temporalidad;
- claim_type;
- tenant;
- trazabilidad.

---

## 3. Claim types

Los claim types expresan naturaleza epistemológica.

### 3.1 EXTRACTED

Información obtenida directamente desde evidencia.

Ejemplos:

```text
Producto A no tiene costo.
Factura 123 tiene fecha 2026-05-01.
Movimiento bancario de $250.000.
```

Características:

- evidencia directa;
- alta trazabilidad;
- bajo nivel interpretativo.

---

### 3.2 INFERRED

Relación inferida por combinación de señales.

Ejemplos:

```text
Posible erosión de margen.
Riesgo de ruptura de stock.
```

Características:

- surge de patrones;
- requiere confidence;
- puede degradarse o confirmarse.

---

### 3.3 AMBIGUOUS

Información insuficiente o contradictoria.

Ejemplos:

```text
Movimiento posiblemente asociado a retiro personal.
Cliente posiblemente duplicado.
```

Características:

- no debe consolidarse;
- requiere más evidencia;
- activa revisión.

---

### 3.4 HYPOTHESIS

Hipótesis clínica-operacional.

Ejemplos:

```text
Dependencia excesiva de proveedor.
Posible cuello de botella operativo.
```

Características:

- nivel interpretativo alto;
- nunca debe convertirse automáticamente en hecho;
- requiere validación.

---

## 4. Regla crítica de soberanía

Regla formal:

```text
Nada inferido se convierte en FindingRecord SUPPORTED
sin evidencia suficiente,
validación determinística
o revisión humana.
```

El LLM puede sugerir.

Pero:

```text
la memoria soberana pertenece al sistema gobernado.
```

---

## 5. Tipos de nodos

La ontología inicial contempla nodos operacionales y clínico-semánticos.

---

## 5.1 Nodos organizacionales

### Tenant

Representa aislamiento multiempresa.

Campos conceptuales:

```text
id
name
created_at
status
```

---

### Empresa

Entidad empresarial concreta.

Puede existir separación futura entre tenant técnico y empresa operacional.

---

## 5.2 Nodos documentales

### ReceptionRecord

Entrada inicial del laboratorio.

Ejemplos:

- audio;
- mensaje;
- upload;
- consulta.

---

### Evidence

Evidencia asociada.

Ejemplos:

- Excel;
- PDF;
- extracto bancario;
- factura;
- captura;
- documento textual.

---

### Documento

Documento estructurado o parseado.

---

## 5.3 Nodos operacionales

### Producto

Entidad comercial individual.

---

### FamiliaDeArticulos

Agrupación operacional/comercial.

---

### Cliente

Entidad comercial compradora.

---

### Proveedor

Entidad proveedora.

---

### CuentaBancaria

Cuenta financiera relevante.

---

### Movimiento

Movimiento financiero u operacional.

---

### Variable

Variable diagnóstica.

Ejemplos:

```text
margen_bruto
rotacion_stock
variacion_costo
```

---

### Formula

Fórmula diagnóstica u operacional.

Ejemplos:

```text
margen_bruto
punto_equilibrio
rotacion_stock
```

---

### Evento

Hecho temporal relevante.

Ejemplos:

```text
suba_precio
ruptura_stock
caida_ventas
```

---

### Proceso

Proceso operacional.

Ejemplos:

```text
compras
ventas
produccion
conciliacion
```

---

## 5.4 Nodos clínico-semánticos

### Sintoma

Expresión observable.

Ejemplos:

```text
vendo mucho pero no queda plata
faltante de stock
```

---

### Patologia

Patrón estructural recurrente.

Ejemplos:

```text
margen_erosionado
riesgo_financiero
cuello_botella
```

---

### Treatment

Intervención operacional.

Ejemplos:

```text
recalcular_lista_precios
automatizar_conciliacion
```

---

### Practice

Práctica PyME.

Puede ser positiva o negativa.

---

### OperationalCase

Caso clínico-operacional consolidado.

---

### Finding

Hallazgo operacional.

---

### PreguntaClinica

Pregunta activada por contexto.

Ejemplos:

```text
Tenés costos actualizados?
Qué porcentaje representa este proveedor?
```

---

## 5.5 Nodos técnicos

### Microservice

Servicio operacional ejecutable.

Ejemplos:

```text
conciliador_bancario
reparador_excel
analizador_stock
```

---

## 6. Tipos de relaciones

SmartGraph necesita relaciones tipadas.

No alcanza con:

```text
A relacionado con B
```

Debe expresarse:

```text
qué tipo de vínculo existe
```

---

## 6.1 Relaciones de evidencia

### EXTRACTED_FROM

```text
Variable → Evidence
```

---

### EVIDENCE_OF

```text
Evidence → Patologia
```

---

### CONFIRMADO_POR

```text
Finding → Evidence
```

---

### OBSERVADO_EN

```text
Evento → Documento
```

---

## 6.2 Relaciones inferenciales

### INFERIDO_DESDE

```text
Patologia → Variable
```

---

### INDICATES

```text
Sintoma → Patologia
```

---

### ACTIVA_PATOLOGIA

```text
Variable → Patologia
```

---

### SOPORTA_HALLAZGO

```text
Evidence → Finding
```

---

## 6.3 Relaciones clínicas

### REQUIRES_EVIDENCE

```text
Patologia → Evidence
```

---

### REQUIRES_VARIABLE

```text
Patologia → Variable
```

---

### SE_CALCULA_CON

```text
Formula → Variable
```

---

### SUGIERE_TRATAMIENTO

```text
Patologia → Treatment
```

---

### REQUIERE_REVISION_HUMANA

```text
Finding → HumanReview
```

Conceptualmente puede existir aunque HumanReview aún no sea entidad formal.

---

## 6.4 Relaciones causales

### CAUSES

```text
Evento → Evento
```

---

### AFFECTS

```text
Variable → Variable
```

---

### DEPENDS_ON

```text
Producto → Proveedor
```

---

### CONTRADICTS

```text
Evidence → Evidence
```

---

### EMPEORA

```text
Evento → Patologia
```

---

### MEJORA

```text
Treatment → Patologia
```

---

### DERIVA_EN

```text
Patologia → Patologia
```

---

## 7. Cardinalidades

SmartGraph debe soportar:

- 1 a 1;
- 1 a muchos;
- muchos a muchos.

---

### 7.1 Uno a uno

Ejemplo:

```text
Finding → SeverityProfile
```

---

### 7.2 Uno a muchos

Ejemplo:

```text
Tenant → ReceptionRecords
Patologia → RequiredEvidence
```

---

### 7.3 Muchos a muchos

Ejemplos:

```text
Pathology ↔ Formula
Pathology ↔ Symptom
Formula ↔ Practice
Treatment ↔ Pathology
Finding ↔ Evidence
Movimiento ↔ Riesgo
```

Esto es esencial porque las patologías empresariales son multifactoriales.

---

## 8. Canonical entities y aliases

La PyME habla ambiguamente.

SmartGraph debe resolver entidades canónicas.

Ejemplo:

```text
stock
mercadería
inventario
depósito
cosas
```

Pueden resolverse como:

```text
canonical_id: product_stock
```

Con aliases:

```text
mercadería
stock
inventario
depósito
cosas
```

---

## 9. Entity resolution

Entity resolution debe contemplar:

- similitud textual;
- contexto operacional;
- historial del tenant;
- evidencia previa;
- confidence;
- validación humana;
- colisiones semánticas.

Ejemplo:

```text
“Mercado Pago”
vs
“mercado”
```

No siempre representan la misma entidad.

---

## 10. Confidence

Toda relación inferencial debe expresar confidence.

Ejemplo conceptual:

```text
0.0 → imposible
0.3 → débil
0.6 → probable
0.9 → muy fuerte
```

El confidence no reemplaza evidencia.

Solo expresa fuerza inferencial.

---

## 11. Temporalidad

Todo nodo o edge relevante debe poder expresar:

```text
tenant_id
source_id
confidence
claim_type
valid_from
valid_until
observed_at
created_at
updated_at
evidence_ids
```

Esto permite:

- evolución histórica;
- memoria longitudinal;
- auditoría;
- reversibilidad;
- análisis temporal.

---

## 12. Subgrafos clínicos

SmartGraph debe permitir activación de subgrafos.

Ejemplo:

```text
subgrafo_financiero
subgrafo_margen
subgrafo_stock
subgrafo_conciliacion
```

Un subgrafo puede activarse por:

- síntoma;
- evidencia;
- pregunta clínica;
- fórmula;
- hallazgo.

---

## 13. Comunidades emergentes

Las comunidades no son solamente carpetas manuales.

Pueden emerger por:

- densidad relacional;
- coocurrencia;
- causalidad repetida;
- dependencia;
- frecuencia operacional.

Ejemplos:

```text
cluster_financiero
cluster_comercial
cluster_stock
cluster_automatizacion
```

---

## 14. God nodes

Un nodo hiperconectado puede indicar:

- dependencia crítica;
- concentración de riesgo;
- cuello de botella;
- centralidad operacional.

Ejemplos:

```text
proveedor dominante
cliente dominante
producto estrella
cuenta bancaria principal
```

Ejemplo clínico:

```text
70% del margen depende de un proveedor.
→ dependencia comercial crítica
```

---

## 15. Activación contextual

La activación contextual debe permitir:

```text
síntoma
→ patologías probables
→ fórmulas relevantes
→ evidencia faltante
→ tratamientos frecuentes
→ preguntas clínicas
```

Ejemplo:

```text
“vendo mucho pero no queda plata”
```

Activa:

```text
margen_erosionado
variacion_costo
productos_sin_costo
precios_desactualizados
```

Y preguntas:

```text
Tenés costos actualizados?
Tenés lista de precios vigente?
```

---

## 16. Separación entre IA y soberanía

El LLM:

- interpreta;
- clasifica;
- sugiere;
- infiere;
- rankea.

Pero:

```text
la persistencia soberana pertenece al sistema determinístico.
```

El LLM nunca debería:

- convertir hipótesis en hechos;
- alterar evidencia original;
- consolidar memoria sin gobernanza;
- escribir directo en estado crítico.

---

## 17. SQL y representación de grafo

La ontología no obliga a usar Neo4j ni motor de grafos dedicado.

En fases iniciales puede persistirse mediante:

- Postgres;
- Supabase;
- tablas relacionales;
- JSONB;
- edges tipados;
- vistas;
- materializaciones.

Lo importante no es el motor.

Es preservar:

```text
entidades
+ relaciones
+ tiempo
+ evidence
+ confidence
+ claim_type
```

---

## 18. Frase rectora

```text
SmartGraph no guarda solo datos.
Guarda estructura operacional viva.
```

---

## 19. Cierre

La ontología SmartGraph es la base semántica para transformar SmartPyme en:

```text
motor clínico-operacional con memoria estructural empresarial
```

El objetivo no es construir un “chat inteligente”.

El objetivo es modelar:

- comportamiento empresarial;
- evidencia;
- relaciones;
- patologías;
- tratamientos;
- evolución temporal;
- activación contextual.

Con separación explícita entre:

```text
hecho
inferido
ambiguo
hipótesis
```

Y con soberanía determinística sobre la memoria persistente.
