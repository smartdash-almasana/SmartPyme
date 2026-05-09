# SmartPyme — SmartGraph: Arquitectura Conceptual

Fecha: 2026-05-09  
Estado: Documento arquitectónico conceptual  
Ámbito: SmartPyme / Laboratorio PyME / Motor clínico-operacional  
Relación: ADR-004 Harness Engineering

---

## 1. Tesis central

SmartGraph es la capa de memoria estructural persistente de SmartPyme.

No reemplaza al motor clínico-operacional.
No reemplaza a BEM.
No reemplaza a Supabase.
No convierte al LLM en fuente de verdad.

SmartGraph introduce una capa anterior al razonamiento clínico:

```text
Raw / Evidence
→ BEM / extracción documental
→ SmartGraph / memoria estructural persistente
→ activación contextual
→ motor clínico-operacional
→ OperationalCase
→ FindingRecord
→ informe / tratamiento
```

La decisión conceptual es:

```text
El LLM no es la memoria.
El grafo es la memoria estructural.
El LLM es intérprete temporal.
El sistema determinístico gobierna persistencia y verdad operacional.
```

---

## 2. Por qué SmartGraph existe

SmartPyme no puede limitarse a analizar archivos aislados.

Una PyME real no expresa sus problemas como datasets limpios.
Los expresa como:

- frases ambiguas;
- Excel vivos;
- PDFs;
- facturas;
- extractos;
- movimientos;
- listas de precios;
- síntomas económicos;
- procesos informales;
- evidencia incompleta;
- decisiones tomadas a ojo.

El problema no es solamente extraer datos.
El problema es conservar estructura operacional a lo largo del tiempo.

SmartGraph existe para convertir evidencia dispersa en una memoria relacional viva:

```text
documentos
+ entidades
+ relaciones
+ eventos
+ evidencia
+ inferencias
+ hipótesis
+ tiempo
+ confidence
+ tenant_id
```

---

## 3. Diferencia entre chunks y topología

Un enfoque basado solo en chunks responde:

```text
¿Dónde aparece este texto?
¿Qué fragmento parece relevante?
```

SmartGraph responde:

```text
¿Qué entidades existen?
¿Cómo se relacionan?
Qué evidencia soporta cada relación?
Qué inferencias son débiles?
Qué comunidades aparecen?
Qué nodo concentra dependencia sistémica?
Qué cambió en el tiempo?
Qué subgrafo activa una patología?
```

Los chunks pueden servir para recuperación textual.
Pero no alcanzan para modelar comportamiento operativo.

SmartGraph agrega topología:

```text
nodos
+ edges tipados
+ dirección
+ temporalidad
+ confidence
+ evidencia
+ causalidad parcial
+ activación contextual
```

---

## 4. Relación con Graphify

Graphify inspira SmartGraph, pero no se copia literalmente.

Lo valioso de Graphify es su enfoque de mapa cognitivo:

```text
detect
→ extract
→ build
→ cluster
→ analyze
→ report
→ export
```

La adaptación SmartPyme absorbe estos principios:

1. Persistencia estructural.
2. Relaciones tipadas.
3. Separación evidencia / inferencia / hipótesis.
4. Entity resolution.
5. Temporalidad.
6. Incremental updates.
7. Clustering emergente.
8. Activación contextual.
9. Memoria longitudinal empresarial.

Diferencia fundamental:

```text
Graphify modela repositorios/documentos.
SmartGraph modela una empresa viva.
```

SmartPyme no necesita solo un grafo documental.
Necesita una memoria clínico-operacional del organismo PyME.

---

## 5. Planos que SmartGraph une

SmartGraph une dos planos que hasta ahora podían aparecer separados.

### 5.1 Plano operacional

Incluye entidades concretas:

- facturas;
- productos;
- familias de artículos;
- movimientos;
- cuentas bancarias;
- ventas;
- costos;
- stock;
- proveedores;
- clientes;
- procesos;
- documentos;
- evidencias;
- eventos.

### 5.2 Plano clínico-semántico

Incluye entidades interpretativas:

- síntoma;
- patología;
- fórmula;
- práctica PyME;
- tratamiento;
- pregunta clínica;
- riesgo;
- cuello de botella;
- automatización posible;
- OperationalCase;
- FindingRecord.

El valor aparece cuando ambos planos se conectan.

Ejemplo:

```text
ventas_altas
+ costos_desactualizados
+ productos_sin_costo
+ margen_bajo
→ activa patología posible: margen erosionado
```

---

## 6. Evidencia, inferencia, ambigüedad e hipótesis

SmartGraph debe separar tipos de claim.

### EXTRACTED

Dato extraído directamente de evidencia.

Ejemplo:

```text
Producto A no tiene costo asociado en el Excel.
```

### INFERRED

Conclusión sugerida por combinación de señales.

Ejemplo:

```text
Posible erosión de margen.
```

### AMBIGUOUS

Señal no resoluble todavía.

Ejemplo:

```text
Movimiento bancario posiblemente asociado a retiro, pero sin documento suficiente.
```

### HYPOTHESIS

Hipótesis clínica-operacional pendiente de validación.

Ejemplo:

```text
Puede existir dependencia excesiva de proveedor.
```

Regla crítica:

```text
Nada inferido se convierte en FindingRecord SUPPORTED sin evidencia suficiente,
validación determinística o revisión humana.
```

---

## 7. Activación contextual

SmartGraph no solo guarda memoria.
También activa contexto relevante.

Entrada del dueño:

```text
“vendo mucho pero no queda plata”
```

SmartGraph debería activar:

- patologías compatibles;
- fórmulas relevantes;
- evidencia faltante;
- casos similares;
- prácticas frecuentes;
- tratamientos históricos;
- repreguntas clínicas;
- subgrafos de ventas, costos, margen y precios.

Ejemplo de activación:

```text
margen_erosionado
→ requiere_formula → margen_bruto
→ requiere_formula → variacion_costo
→ requiere_evidencia → ventas
→ requiere_evidencia → costos
→ asociado_a_sintoma → vendo_mucho_no_queda_plata
→ sugiere_tratamiento → recalcular_lista_precios
```

---

## 8. Entity resolution

Entity resolution es crítico porque la PyME habla de forma ambigua.

Ejemplo:

```text
mercadería
stock
inventario
depósito
cosas
```

Pueden apuntar a una entidad canónica:

```text
canonical_id: product_stock
aliases:
  - mercadería
  - stock
  - inventario
  - depósito
  - cosas
```

SmartGraph debe distinguir:

- nombre textual;
- alias;
- entidad canónica;
- tenant_id;
- confidence;
- evidencia fuente;
- estado de resolución.

Esto evita duplicar memoria y permite activar contexto aunque el dueño use lenguaje informal.

---

## 9. Temporalidad viva

SmartPyme necesita temporalidad empresarial viva, no un grafo estático.

Cada nodo o edge relevante debería poder expresar:

- tenant_id;
- source_id;
- confidence;
- valid_from;
- valid_until;
- observed_at;
- created_at;
- updated_at;
- evidence_ids;
- claim_type.

Ejemplo:

```text
Producto A tenía margen bajo en marzo.
Producto A recuperó margen en abril luego de actualizar lista de precios.
```

Sin temporalidad, SmartGraph no puede distinguir:

```text
estado actual
vs
estado histórico
vs
patrón recurrente
```

---

## 10. Memoria longitudinal empresarial

SmartGraph permite construir historia operacional por tenant.

A través del tiempo, puede registrar:

- dolores recurrentes;
- evidencia frecuente;
- evidencia faltante;
- patologías repetidas;
- tratamientos aplicados;
- hallazgos previos;
- mejoras observadas;
- deterioros;
- proveedores críticos;
- productos centrales;
- procesos frágiles;
- automatizaciones candidatas.

La empresa deja de ser un conjunto de archivos.

Pasa a ser un organismo operacional con memoria estructural.

---

## 11. Comunidades y clusters emergentes

SmartGraph debe permitir detectar comunidades.

Ejemplos:

### Comunidad financiera

```text
caja
banco
MercadoPago
conciliación
cobros
transferencias
retiros
```

### Comunidad comercial

```text
ventas
margen
precios
clientes
productos
familias de artículos
```

### Comunidad operacional

```text
stock
depósito
producción
SKU
mermas
movimientos
```

Las comunidades no deben ser solo categorías manuales.
También pueden emerger por topología.

Una comunidad puede revelar:

- cluster de margen;
- cluster financiero;
- cluster de stock;
- cluster de automatización;
- cluster de erosión comercial.

---

## 12. Nodos hiperconectados o god nodes

En una PyME, un nodo hiperconectado puede revelar dependencia sistémica.

Ejemplos:

- proveedor crítico;
- producto estrella;
- cliente dominante;
- cuenta bancaria principal;
- empleado clave;
- proceso central;
- familia de artículos dominante.

Ejemplo:

```text
70% del margen depende de 1 proveedor.
```

Esto puede activar una patología:

```text
dependencia comercial crítica
```

Un god node no es bueno ni malo por sí mismo.
Es una señal estructural que requiere interpretación clínica-operacional.

---

## 13. SQL como persistencia y grafo como conocimiento

SmartGraph no obliga a abandonar SQL.

Supabase/Postgres puede seguir siendo la persistencia operativa principal.

La decisión conceptual es:

```text
SQL persiste registros y contratos.
SmartGraph expresa conocimiento relacional, activación y topología.
```

En fase inicial, SmartGraph puede vivir como:

- tablas relacionales de nodos y edges;
- vistas materializadas;
- JSONB controlado;
- exportaciones graph.json;
- índices por tenant;
- mecanismos de activación contextual.

No es obligatorio incorporar una base de grafos desde el inicio.

Lo obligatorio es preservar el modelo mental de grafo:

```text
entidades + relaciones + evidencia + tiempo + confidence
```

---

## 14. Relación con BEM

BEM no es el cerebro.

BEM es la capa de ingesta y estructuración documental.

BEM hace:

- parsing;
- OCR si aplica;
- extracción;
- estructura documental;
- normalización inicial.

SmartGraph hace:

- entidades;
- relaciones;
- eventos;
- evidencia;
- tiempo;
- confidence;
- canonical entities;
- activación contextual.

Motor clínico-operacional hace:

- interpreta operacionalmente;
- activa patologías;
- ejecuta fórmulas;
- genera casos;
- genera hallazgos.

---

## 15. Relación con Harness Engineering

SmartGraph debe operar dentro del principio de Harness Engineering.

Esto implica:

```text
LLM interpreta, sugiere e infiere.
Harness valida, limita, registra y bloquea.
SmartGraph conserva memoria estructural.
```

El LLM no debe escribir directamente en memoria soberana.

Debe producir candidatos:

- relación candidata;
- entidad candidata;
- hipótesis candidata;
- clasificación candidata;
- alias candidato.

Luego el sistema determinístico, las reglas de confianza o la revisión humana deciden si se persiste y con qué claim_type.

---

## 16. Many-to-many clínico-operacional

SmartGraph debe soportar relaciones muchos-a-muchos.

Ejemplos:

```text
Pathology ↔ Formula
Pathology ↔ Symptom
Formula ↔ Practice
Treatment ↔ Pathology
Finding ↔ Evidence
Finding ↔ Pathology
Movement ↔ Risk
```

Esto es esencial porque una patología no se activa por una sola señal.
Y una evidencia puede participar en múltiples hipótesis.

Ejemplo:

```text
productos_sin_costo
```

Puede participar en:

- margen erosionado;
- imposibilidad de calcular rentabilidad;
- lista de precios deteriorada;
- riesgo de decisión comercial a ciegas.

---

## 17. SmartPyme como sistema clínico-operacional

Con SmartGraph, SmartPyme deja de ser:

```text
herramienta que analiza archivos
```

Y empieza a ser:

```text
sistema clínico-operacional con memoria estructural empresarial
```

La empresa se modela como organismo dinámico:

| Concepto clínico | SmartPyme |
|---|---|
| estudios | evidencias |
| síntomas observados | hallazgos |
| patologías | patrones estructurales recurrentes |
| instrumentos diagnósticos | fórmulas |
| tratamientos | intervenciones operacionales |
| hábitos | prácticas PyME |
| historia clínica | memoria longitudinal por tenant |
| sistema nervioso | SmartGraph |

---

## 18. Límites explícitos

Este documento no decide implementación inmediata.

No implica:

- instalar Graphify en producción;
- reemplazar Supabase;
- reemplazar BEM;
- modificar contratos actuales;
- meter grafo en código sin ADR específico;
- permitir que el LLM escriba directo en memoria;
- rediseñar lo ya cerrado.

---

## 19. Decisiones pendientes

Antes de implementar, se debe decidir si SmartGraph entra como:

```text
A. módulo propio interno
B. wrapper inicial de Graphify
C. spike experimental sobre docs/ y contracts/
D. Capa 0 persistida en Supabase/SQLite
```

La recomendación inicial es no saltar a código.

Primero deben quedar escritos:

1. arquitectura conceptual;
2. ontología y relaciones;
3. ADR de adopción técnica;
4. spike acotado si corresponde.

---

## 20. Frase rectora

```text
SmartGraph convierte el caos PyME en memoria estructural activable.
```

---

## 21. Cierre

SmartGraph es la pieza que permite que SmartPyme no dependa de memoria conversacional ni de intuición del modelo.

El sistema puede recibir lenguaje ambiguo, documentos incompletos y evidencia dispersa, pero conservar estructura:

```text
qué se observó,
de dónde salió,
qué significa,
qué tan confiable es,
qué activa,
qué falta,
y cómo evoluciona en el tiempo.
```

Ese es el puente entre el Laboratorio PyME y un verdadero sistema operativo clínico-operacional.
