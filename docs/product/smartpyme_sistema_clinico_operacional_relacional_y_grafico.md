# SMARTPYME — SISTEMA CLÍNICO-OPERACIONAL RELACIONAL Y GRÁFICO

## Estado

DOCUMENTO RECTOR — DESIGN_FULL

Modo:
- No implementación
- No migración
- No endpoint
- No cambios de runtime
- No cambios en Supabase
- No cambios en API
- No cambios en engine actual

Este documento redefine SmartPyme como:

```text
Sistema Clínico-Operacional Relacional y Gráfico
```

No es un chatbot.

No es un ERP.

No es un dashboard.

No es únicamente un sistema de procesamiento documental.

Es un sistema de:

```text
recepción,
absorción,
estructuración,
relación,
memoria,
inferencia,
detección patológica,
y producción de hallazgos accionables.
```

---

# 1. Principio arquitectónico

## 1.1 Tesis central

La empresa se modela como:

```text
organismo operacional vivo
```

El objetivo del sistema no es solamente:

```text
leer documentos
```

sino:

```text
comprender relaciones operacionales,
detectar síntomas,
construir hipótesis,
contrastar evidencia,
identificar patologías,
y producir claridad accionable.
```

---

# 1.2 Separación IA vs núcleo determinístico

## IA

La IA:

```text
interpreta
clasifica
extrae
sugiere
infiere
prioriza
```

La IA NO:

```text
persiste verdad
abre casos clínicos finales
confirma patologías
modifica historia clínica
emite hallazgos soberanos sin evidencia
```

---

## Núcleo determinístico

El núcleo determinístico:

```text
gobierna contratos
persiste relaciones
versiona conocimiento
resuelve entidades
controla evidencia
mantiene trazabilidad
controla estados
preserva temporalidad
```

---

# 1.3 SmartGraph

SmartGraph es:

```text
la capa de memoria estructural persistente
```

No es visualización.

No es únicamente un knowledge graph.

Es:

```text
el sistema nervioso relacional de SmartPyme.
```

SmartGraph conserva:

- entidades
- relaciones
- evidencia
- hipótesis
- causalidad
- temporalidad
- comunidades operacionales
- comunidades patológicas
- dependencias sistémicas
- contradicciones
- historial evolutivo

---

# 1.4 Conversación clínica

La conversación NO es chat.

La conversación es:

```text
rampa clínica operacional
```

Sirve para:

- capturar síntomas
- detectar lenguaje PyME
- clasificar dolor
- solicitar evidencia
- construir hipótesis
- abrir casos
- enriquecer contexto
- detectar bloqueos

---

# 1.5 Evidencia soberana

Sin evidencia trazable:

```text
no existe hallazgo clínico-operacional válido
```

Todo hallazgo debe poder vincularse a:

- documento
- extracción
- variable
- fórmula
- relación
- timestamp
- tenant

---

# 2. Arquitectura macro

```text
[ Caos PyME ]
       ↓
[ Reception Layer ]
       ↓
[ IA de extracción ]
       ↓
[ SmartGraph ]
       ↓
[ Comunidades emergentes ]
       ↓
[ Motor clínico ]
       ↓
[ OperationalCaseCandidate ]
       ↓
[ Hallazgos ]
       ↓
[ Tratamientos / acciones ]
```

---

# 3. SmartGraph — Modelo relacional gráfico

## 3.1 Nodo

Un nodo representa:

```text
una unidad significativa del organismo empresarial
```

Tipos posibles:

- tenant
- empresa
- persona
- cliente
- proveedor
- producto
- cuenta
- movimiento
- stock
- documento
- evidencia
- variable
- fórmula
- patología
- síntoma
- tratamiento
- práctica
- hallazgo
- proceso
- workflow
- riesgo
- comunidad

---

# 3.2 Arista

Una arista representa:

```text
una relación explícita o inferida
```

Tipos:

- DEPENDS_ON
- AFFECTS
- CAUSES
- INDICATES
- CONTRADICTS
- OBSERVED_IN
- EXTRACTED_FROM
- REQUIRES_EVIDENCE
- BELONGS_TO
- CORRELATES_WITH
- WORSENS
- IMPROVES
- GENERATED
- VALIDATES
- BLOCKS

---

# 3.3 Tipos de relación

## Uno a uno

```text
Hallazgo
→ tiene
SeverityProfile
```

---

## Uno a muchos

```text
Tenant
→ tiene
ReceptionRecords
```

---

## Muchos a muchos

```text
Patología
↔ Fórmulas

Patología
↔ Síntomas

Síntoma
↔ Evidencia

Tratamiento
↔ Patologías

Fórmula
↔ Variables
```

---

# 3.4 Comunidades

Una comunidad es:

```text
cluster emergente de entidades altamente relacionadas
```

Ejemplos:

## Comunidad financiera

- caja
- banco
- cobranzas
- transferencias
- conciliación
- deuda

---

## Comunidad comercial

- ventas
- margen
- listas
- descuentos
- clientes
- familias

---

## Comunidad operacional

- stock
- depósito
- SKU
- producción
- mermas
- logística

---

# 3.5 God Nodes

God Nodes:

```text
nodos sistémicamente críticos
```

Ejemplos:

- proveedor dominante
- producto estrella
- cliente dominante
- cuenta bancaria central
- empleado clave

Sirven para:

```text
detectar dependencia sistémica
```

---

# 3.6 Tipos de evidencia relacional

## EXTRACTED

Dato directamente observado.

Ejemplo:

```text
Producto sin costo
```

---

## INFERRED

Hipótesis generada.

Ejemplo:

```text
Posible erosión de margen
```

---

## AMBIGUOUS

Relación posible no validada.

Ejemplo:

```text
Posible fuga de caja
```

---

# 3.7 Temporalidad

Toda relación debe poder registrar:

- valid_from
- valid_to
- observed_at
- changed_at
- evidence_timestamp

La empresa se modela como:

```text
organismo evolutivo
```

No como snapshot estático.

---

# 4. Modelo clínico-operacional

## 4.1 Patología

Una patología es:

```text
patrón recurrente de relaciones problemáticas
```

Ejemplos:

- margen erosionado
- stock inmovilizado
- dependencia crítica proveedor
- caja inconsistente
- cuello de botella operativo
- costos desalineados
- exceso administrativo manual

---

# 4.2 Síntoma

Un síntoma es:

```text
manifestación observable del problema
```

Ejemplos:

- vendo mucho pero no queda plata
- falta stock frecuente
- diferencias banco
- listas atrasadas
- carga manual excesiva

---

# 4.3 Fórmulas

Las fórmulas son:

```text
instrumentos diagnósticos
```

Ejemplos:

```text
margen = (precio - costo) / precio

rotación_stock

ROI

costo_reposición

cashflow operativo
```

---

# 4.4 Tratamiento

El tratamiento representa:

```text
acción correctiva operacional
```

Ejemplos:

- actualizar listas
- automatizar conciliación
- segmentar stock
- renegociar proveedor
- recalcular costos

---

# 5. Modelo BEM → SmartPyme

BEM:

```text
estructura evidencia
```

SmartPyme:

```text
interpreta clínicamente
```

BEM nunca diagnostica.

---

# 5.1 Entidades

## document_ingestions

Representa ingreso documental.

---

## bem_workflows

Representa workflow ejecutado.

---

## bem_calls

Representa llamadas realizadas.

---

## bem_events

Representa eventos emitidos.

---

## bem_extraction_outputs

Representa salida estructurada.

---

## extracted_entities

Entidades detectadas.

---

## extracted_variables

Variables detectadas.

---

## extracted_evidence

Evidencia estructurada.

---

## evidence_source_links

Relación evidencia ↔ documento.

---

## variable_observations

Observaciones temporales.

---

## document_quality_signals

Calidad documental.

---

## human_review_required

Necesidad de revisión humana.

---

# 5.2 Flujo conceptual

```text
BEM output
→ evidencia
→ variables
→ fórmulas
→ modelos
→ grafos causales
→ hipótesis
→ hallazgos posibles
```

---

# 6. Rampa conversacional clínica

## Etapa 1 — Relato libre

Ejemplo:

```text
“Vendo mucho y no queda plata.”
```

---

## Etapa 2 — Anamnesis

Preguntas:

- ¿Desde cuándo?
- ¿Qué cambió?
- ¿Hay costos actualizados?
- ¿Qué sistema usan?
- ¿Cómo manejan stock?

---

## Etapa 3 — Captura estructurada

Se registran:

- síntomas
- contexto
- rubro
- tamaño
- urgencia
- restricciones

---

## Etapa 4 — Hipótesis iniciales

Ejemplos:

- erosión margen
- desorden costos
- conciliación incompleta

---

## Etapa 5 — Pedido de evidencia

El sistema solicita:

- ventas
- costos
- bancos
- stock
- listas

---

## Etapa 6 — Ingesta documental

Documentos ingresan a BEM.

---

## Etapa 7 — Extracción

Se generan:

- entidades
- variables
- relaciones
- señales

---

## Etapa 8 — Contraste

El sistema compara:

```text
relato humano
VS
realidad documental
```

---

## Etapa 9 — Brechas

Ejemplos:

```text
Dueño afirma rentabilidad positiva
pero margen calculado es negativo.
```

---

## Etapa 10 — OperationalCaseCandidate

Representa:

```text
hipótesis clínica razonable
```

Todavía NO confirmada.

---

## Etapa 11 — OperationalCase

Caso clínico validado.

---

## Etapa 12 — Hallazgo

Salida accionable.

---

# 7. Ejemplos clínicos

# 7.1 Margen erosionado

## Síntoma

```text
“Vendo mucho pero no queda plata.”
```

---

## Evidencia requerida

- ventas
- costos
- listas
- facturas proveedor

---

## Variables

- precio
- costo
- margen
- inflación proveedor

---

## Fórmulas

```text
margen bruto
margen neto
variación costo
```

---

## Posibles hallazgos

- productos sin costo
- listas atrasadas
- margen negativo oculto

---

## Bloqueos

Sin costos:

```text
BLOCKED
```

---

# 7.2 Caja inconsistente

## Síntoma

```text
“No me cierra la caja.”
```

---

## Evidencia

- banco
- caja
- MP
- transferencias

---

## Variables

- ingresos
- egresos
- conciliación

---

## Hallazgos

- movimientos sin trazabilidad
- cobros faltantes
- duplicaciones

---

# 7.3 Stock inmovilizado

## Síntoma

```text
“Hay mercadería parada.”
```

---

## Variables

- rotación
- antigüedad
- ventas

---

## Hallazgos

- familias sin movimiento
- sobrecompra
- capital inmovilizado

---

# 8. Reglas de decisión

# 8.1 Qué decide BEM

BEM:

- extrae
- estructura
- clasifica documentos
- identifica entidades

BEM NO:

- diagnostica
- interpreta negocio
- confirma patologías

---

# 8.2 Qué decide SmartPyme

SmartPyme:

- interpreta
- correlaciona
- genera hipótesis
- detecta patrones
- abre casos
- prioriza hallazgos

---

# 8.3 Qué requiere humano

- validación final
- decisiones estratégicas
- acciones sensibles
- confirmación contextual

---

# 8.4 Cuándo se bloquea

El sistema se bloquea cuando:

- falta evidencia crítica
- hay contradicción grave
- confidence insuficiente
- temporalidad inválida

---

# 9. Riesgos

## Riesgo

Convertir todo en JSON opaco.

### Mitigación

SmartGraph explícito.

---

## Riesgo

Diagnóstico sin evidencia.

### Mitigación

Estados BLOCKED.

---

## Riesgo

Dependencia de BEM.

### Mitigación

BEM solo estructura.

---

## Riesgo

Hardcodear patologías.

### Mitigación

Catálogo versionado.

---

## Riesgo

Sobrediseño teórico.

### Mitigación

Microservicios reales.

---

# 10. Relación con arquitectura existente

Este documento:

- extiende ADR-002
- complementa conversation_sessions P0
- expande OperationalCase
- prepara OperationalCaseCandidate
- formaliza SmartGraph

No reemplaza:

- engine actual
- hipótesis actuales
- contracts existentes

Los recontextualiza.

---

# 11. Primer artefacto técnico posterior

## Recomendación

Crear:

```text
ADR-003-smartgraph-clinical-memory-layer.md
```

Objetivo:

Formalizar:

- contratos de nodos
- contratos de aristas
- tipos de evidencia
- temporalidad
- confidence
- comunidades
- inferencia
- canonical entities

Sin implementación todavía.

---

# 12. Cierre

SmartPyme deja de modelarse como:

```text
chatbot + documentos
```

Y pasa a modelarse como:

```text
sistema clínico-operacional
con memoria estructural persistente
```

El LLM deja de ser:

```text
la memoria
```

Y pasa a ser:

```text
intérprete temporal
```

La memoria real vive en:

```text
SmartGraph
```

El grafo preserva:

- relaciones
- causalidad
- temporalidad
- evidencia
- historia
- comunidades
- patologías
- tratamientos

La conversación captura síntomas.

La evidencia valida.

El grafo recuerda.

El motor clínico interpreta.

Y SmartPyme evoluciona hacia:

```text
Sistema Operativo Clínico-Operacional PyME
```

