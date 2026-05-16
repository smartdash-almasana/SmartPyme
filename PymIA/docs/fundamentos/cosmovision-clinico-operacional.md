# ADR-005 — Cosmovisión Clínico-Operacional de SmartPyme

## Estado

Aceptado como marco arquitectural conceptual.

Este documento no implementa código. Define la cosmovisión técnica y epistemológica que debe orientar las próximas capas de SmartPyme.

---

## 1. Tesis central

SmartPyme no debe ser entendido como un auditor de Excel ni como un chatbot de gestión.

SmartPyme debe evolucionar como un **sistema clínico-operacional** capaz de convertir datos fragmentados de una PyME en una estructura de verdad operativa, auditable, contextual y accionable.

La finalidad no es obtener certezas absolutas.

La finalidad es **sostener la duda operacional** hasta convertirla en acción acertiva certificada por el dueño.

```text
Duda sostenida
→ hipótesis relacional
→ clarificación
→ acción orientada a ROI
→ validación del dueño
→ acertividad acumulada
```

---

## 2. Principio rector

```text
La duda dinamiza el sistema.
La acertividad lo orienta.
El dueño certifica el acierto.
```

El sistema invierte energía computacional, conversacional y operativa. Esa energía solo se justifica si conduce a mayor ROI operacional, menor pérdida, mejor decisión, ahorro de tiempo o reducción de riesgo.

La única certeza válida no es teórica: es la **acertividad operativa certificada por el dueño o dueños de la PyME**.

---

## 3. Relación con la arquitectura canónica

Este ADR respeta la ley arquitectónica vigente:

```text
IA interpreta; kernel decide.
```

Y se integra al pipeline canónico:

```text
Ingesta
→ Normalización
→ Entity Resolution
→ Clarification
→ Orquestación
→ Comparación
→ Hallazgos
→ Comunicación
→ Acción
```

Hermes se ubica principalmente en:

```text
Clarification
→ Orquestación
→ Comunicación
```

SmartCounter Core conserva la responsabilidad de cálculo, comparación, validación, estados, hallazgos y bloqueo.

---

## 4. Modelo de verdad multi-capa

SmartPyme no opera sobre una verdad plana. Opera sobre cuatro capas concurrentes.

### 4.1 Verdad documental

Base dura del sistema:

- facturas
- bancos
- stock
- ventas
- compras
- PDFs
- planillas
- documentos operativos
- canales externos como MercadoLibre u otros marketplaces

### 4.2 Verdad computada

Datos derivados mediante fórmulas y reglas:

- margen
- ROI
- flujo de caja
- rotación
- aging
- capital inmovilizado
- rentabilidad
- desvíos
- inconsistencias

### 4.3 Verdad del dueño

Criterio humano que contextualiza el dato:

- liquidaciones estratégicas
- tolerancias comerciales
- políticas de descuento
- excepciones
- urgencias de caja
- decisiones tácticas
- prioridades reales
- percepción de riesgo

### 4.4 Verdad temporal

La verdad operacional tiene vigencia.

Un costo, precio, política o interpretación puede ser válido en un período y perder validez luego.

La verdad no solo se almacena; se versiona.

---

## 5. El algoritmo vertebral: sostener la duda

El algoritmo vertebral de SmartPyme no debe ser la obtención inmediata de certezas.

Debe ser la capacidad de sostener dudas útiles y hacerlas circular por el sistema hasta producir una acción acertiva.

Un hallazgo aislado no equivale automáticamente a una patología.

Ejemplo:

```text
VENTA_BAJO_COSTO
```

Puede significar:

- descapitalización
- error de costeo
- liquidación estratégica
- urgencia de caja
- limpieza de stock muerto
- política comercial temporal

Por lo tanto:

```text
hallazgo ≠ diagnóstico final
```

El hallazgo es una señal. La patología emerge del contexto, las relaciones, la temporalidad y la validación humana.

---

## 6. SmartGraph: grafo dinámico de inferencia operacional

SmartGraph debe ser entendido como la capa relacional que permite modelar tensión operacional, causalidad no lineal, contradicciones y memoria persistida.

No debe limitarse a entidades planas.

Debe poder representar:

- entidades
- eventos
- relaciones
- hipótesis
- contradicciones
- nodos de tensión
- causalidades posibles
- explicaciones alternativas
- vigencia temporal
- criterios del dueño
- acciones
- resultados

### 6.1 Nodos

Ejemplos de nodos:

- producto
- cliente
- proveedor
- venta
- compra
- deuda
- stock
- margen
- hallazgo
- señal
- hipótesis
- patología
- tratamiento
- acción
- outcome
- certificación del dueño

### 6.2 Relaciones

Ejemplos de relaciones:

- depende_de
- afecta_a
- causa_posible_de
- contradice
- correlaciona_con
- sustituye_a
- pertenece_a
- explica_a
- requiere_clarificación
- fue_validado_por
- tiene_vigencia

---

## 7. Marco físico-matemático

SmartPyme debe apoyarse conceptualmente en una combinación de marcos físico-matemáticos, sin convertir prematuramente la arquitectura en sobreingeniería.

### 7.1 Teoría de grafos probabilísticos

Modela variables entrecruzadas.

Un problema financiero rara vez tiene una sola causa. Una baja de margen puede estar conectada con inflación, logística, stock, tiempo del dueño, descuentos, proveedor, canal de venta o error documental.

Las aristas pueden incluir:

- peso de confianza
- dirección
- vigencia
- contradicción
- impacto
- fuente

### 7.2 Redes bayesianas

Permiten inferir hipótesis bajo incertidumbre.

Ejemplo:

```text
VENTA_BAJO_COSTO + STOCK_ANTIGUO
```

puede aumentar la probabilidad de:

```text
LIQUIDACION_ESTRATEGICA
```

y disminuir la probabilidad de:

```text
ERROR_DE_COSTEO
```

Hermes puede intervenir para resolver ambigüedad mediante preguntas al dueño.

### 7.3 Sistemas dinámicos y bucles de retroalimentación

Tiempo y dinero deben interpretarse como flujos.

La PyME puede modelarse como un sistema de stocks y flujos:

- stock de capital
- stock de tiempo disponible
- flujo de ventas
- flujo de tareas operativas
- flujo de caja
- flujo de deuda
- flujo de atención del dueño

El sistema debe detectar cuándo el gasto de entropía operacional consume energía que debería alimentar crecimiento, margen o estabilidad.

### 7.4 Lógica difusa

La verdad del dueño rara vez es binaria.

El dueño puede decir:

- "esto fue bastante agresivo"
- "esa factura es medio dudosa"
- "ese proveedor está casi descartado"
- "esa liquidación fue parcialmente estratégica"

La lógica difusa permite convertir criterio humano en rangos computables sin forzar falsos binarismos.

### 7.5 Decaimiento temporal de vigencia

La verdad operacional tiene vida media.

Un costo de hace tres meses puede ser documentalmente verdadero, pero operacionalmente poco vigente en un contexto inflacionario.

Los datos antiguos no deben tratarse como falsos, sino como señales de menor vigencia o mayor entropía.

---

## 8. Topología operacional

SmartPyme debe tender a construir una topología operacional de la PyME.

La PyME no es un conjunto de números. Es un organismo dinámico compuesto por tensiones entre:

- tiempo
- dinero
- stock
- caja
- deuda
- margen
- ventas
- compras
- dependencia
- capacidad operativa
- atención del dueño
- riesgo

El sistema debe aprender a leer la forma del negocio.

```text
forma estable → operación sana
forma deformada → tensión
forma extrema → urgencia
```

---

## 9. Modelo gaussiano operacional

La campana de Gauss opera como metáfora formal del equilibrio operacional.

### 9.1 Centro

En el centro vive la homeostasis operacional:

- margen sostenible
- caja respirable
- stock rotando
- tiempo del dueño controlado
- deuda manejable
- ventas estables

No significa perfección. Significa equilibrio funcional.

### 9.2 Márgenes

En los márgenes aparece la urgencia.

Puede haber urgencia por defecto:

- falta de caja
- caída de ventas
- margen negativo
- stock insuficiente
- deuda vencida

Y urgencia por exceso:

- sobrestock
- capital inmovilizado
- crecimiento desordenado
- concentración de clientes
- saturación del dueño
- ventas que crecen más rápido que la operación

Ambos extremos pueden ser patológicos.

---

## 10. Doble capa de respuesta

SmartPyme debe sostener dos temporalidades simultáneas.

### 10.1 Capa imperativa

Actúa ante urgencias.

Ejemplos:

```text
OJO: sin stock crítico.
OJO: mucho capital en la calle que no retorna.
OJO: productos con precios desactualizados.
OJO: ventas en MercadoLibre cayendo en picada.
```

La capa imperativa protege la supervivencia.

### 10.2 Capa clínica

Interpreta cuadros operacionales.

No reacciona solo a un dato. Cruza señales, contexto, historia, criterios y relaciones.

La capa clínica protege la evolución.

---

## 11. Hermes

Hermes no calcula ni decide verdad final.

Hermes:

- conversa
- clarifica
- sostiene ambigüedad
- resuelve preguntas pendientes
- consulta herramientas
- comunica hallazgos
- captura verdad del dueño
- registra criterios humanos
- acompaña acciones

Definición:

```text
Hermes = mecanismo conversacional de resolución progresiva de ambigüedad.
```

Hermes transforma lenguaje humano en contexto computable para el kernel.

---

## 12. SmartCounter Core

SmartCounter Core:

- calcula
- valida
- bloquea
- compara
- persiste
- detecta señales
- produce hallazgos
- mantiene estados

Si falta información crítica, el flujo debe bloquearse y generar una solicitud de aclaración.

```text
BLOCKED_BY_AMBIGUITY
```

No se debe avanzar hacia diagnóstico cerrado si el sistema detecta ambigüedad crítica.

---

## 13. Contrato conceptual

```text
Fact
→ dato estructurado extraído

Signal
→ anomalía o tensión detectada

Finding
→ señal estructurada con evidencia

Hypothesis
→ interpretación posible

ClarificationRequest
→ pregunta necesaria para reducir ambigüedad

OwnerCriterion
→ verdad del dueño computable

OperationalPicture
→ cuadro operativo estabilizado

Action
→ intervención propuesta

Outcome
→ resultado observado

OwnerCertification
→ validación humana del acierto

AssertivenessScore
→ aprendizaje acumulado de acertividad
```

---

## 14. Criterio de implementación futura

No implementar patologías como simple suma lineal de hallazgos.

Primero debe existir un contrato mínimo para:

- señales
- hipótesis
- relaciones
- ambigüedad
- clarification requests
- criterio del dueño
- vigencia temporal
- cuadro operativo

Las reglas actuales de diagnóstico son válidas como señales iniciales, pero no agotan el modelo clínico-operacional.

---

## 15. Frase canónica

```text
SmartPyme sostiene la duda hasta convertirla en acción acertiva certificada por el dueño.
```

```text
La capa imperativa protege la supervivencia.
La capa clínica protege la evolución.
```
