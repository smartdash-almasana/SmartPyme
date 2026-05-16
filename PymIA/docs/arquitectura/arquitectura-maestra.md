# SmartPyme: Arquitectura Maestra del Sistema Operativo Organizacional

**Versión:** 2.0
**Fecha:** Mayo 2026
**Clasificación:** Canónico, Interno

---

## 1. Resumen Ejecutivo

SmartPyme es un **Sistema Operativo Organizacional conversacional** para PyMEs. No es un chatbot, un asistente de preguntas y respuestas ni una herramienta de automatización de tareas sueltas. Es una plataforma que convierte el dolor difuso del dueño de negocio en hipótesis verificables, evidencia curada, diagnósticos trazables y decisiones registradas.

El principio rector que gobierna todo el diseño es uno solo:

> **SmartPyme no decide. SmartPyme propone. El dueño confirma.**

Sin autorización explícita y trazable del dueño, no hay ejecución.

La arquitectura se fundamenta en una separación clave: un **core operativo estable** y agnóstico del dominio, y **paquetes de dominio (Domain Packs) desmontables** que le otorgan conocimiento especializado. Esto permite que el mismo motor opere en una PyME, una clínica o una fábrica, simplemente cambiando el paquete de conocimiento.

---

## 2. Principios Fundamentales de Interacción

### 2.1. El Dueño en Control: Ciclo de Admisión

La interacción no es un chat transaccional, sino un proceso de anamnesis clínica. La secuencia rectora para construir un caso es invariable:

```
Dueño → Anamnesis → Taxonomía → Variables base → Demanda → Caso operativo inicial
```

El sistema no toma la demanda como una verdad absoluta, sino como el punto de partida para una investigación estructurada.

### 2.2. Priorización por ROI Clínico

El sistema no atiende problemas en orden de llegada, sino de impacto. La prioridad se establece siguiendo un triaje clínico:

1. **SANGRÍA:** Detener la pérdida activa de dinero o recursos.
2. **INESTABILIDAD:** Estabilizar flujos operativos críticos.
3. **OPTIMIZACIÓN:** Mejorar y escalar operaciones ya estables.

### 2.3. Inteligencia Epistemológica

El sistema no trata toda la información como igual. Clasifica cada pieza de evidencia según su estado de certeza:

- **CERTEZA:** El dato es verificable y permite avanzar en el análisis.
- **DUDA:** La información podría existir pero no está confirmada. **Genera una tarea** con responsable, formato y tiempo.
- **DESCONOCIMIENTO:** El dato no existe o es inalcanzable. Se excluye del alcance inicial.

---

## 3. Arquitectura de Conocimiento: Core Estable, Dominio Desmontable

### 3.1. Core Operativo vs. Domain Packs

- **Core Estable:** Contiene la lógica agnóstica para gestionar el flujo de investigación: recepción, conversación, curación, validación de condiciones, creación de casos, reportes, decisiones y trazabilidad.
- **Domain Packs (Paquetes de Dominio):** Módulos desmontables que contienen el conocimiento de un sector o área específica (PyME, Salud, Agro). Incluyen síntomas, patologías, fórmulas y narrativas propias del dominio.

### 3.2. Knowledge Tanks (Tanques de Conocimiento)

Son los componentes granulares que, ensamblados, forman un `Domain Pack`. Puede haber tanques transversales (contabilidad, finanzas) y sectoriales (gastronomía, metalurgia).

### 3.3. Contratos Genéricos con `domain_id`

Para mantener el core agnóstico, los contratos de datos (`OperationalCase`, `DiagnosticReport`) son genéricos. Se especializan en contexto a través de un `domain_id`, que permite al sistema cargar los catálogos y reglas correspondientes.

### 3.4. Roles del Conocimiento

- **Catálogo (SymptomPathologyCatalog):** **Clasifica**. Traduce el "dolor" del dueño en síntomas y patologías candidatas. Su función es orientar la investigación.
- **Knowledge Tank:** **Calcula**. Contiene las fórmulas, métodos y benchmarks para cuantificar el impacto de un hallazgo.
- **Caso (OperationalCase):** **Conecta**. Es el expediente que une la demanda, la patología candidata del catálogo y la evidencia requerida para que el Knowledge Tank pueda ejecutar un cálculo.

---

## 4. Flujo de Investigación Canónico

SmartPyme sigue un proceso riguroso para pasar de la conversación a un resultado auditable.

1. **SymptomPathologyCatalog:** La demanda del dueño se mapea contra este catálogo para identificar una hipótesis investigable.
2. **OperationalCase:** Se crea un expediente técnico para la investigación. Contiene la hipótesis, la evidencia disponible y las variables curadas.
3. **DiagnosticReport:** El motor de análisis ejecuta la investigación y genera este reporte, que contiene los hallazgos (confirmados, descartados o con evidencia insuficiente).
4. **ValidatedCaseRecord:** Una vez cerrado el ciclo, se genera un registro inmutable y auditable del caso completo, vinculando la hipótesis, la evidencia usada, los hallazgos y la decisión del dueño.

---

## 5. Conectividad y Orquestación

### 5.1. MCP Bridge (Multi-Agent Communication Protocol)

Actúa como una capa de "enchufes" segura y estandarizada. Expone las herramientas y capacidades del core de SmartPyme de forma controlada.

### 5.2. Hermes Runtime

Es el agente orquestador que consume las herramientas del MCP Bridge. Orquesta los pasos de un flujo de trabajo (ej. pedir evidencia, esperar, ejecutar un cálculo), pero no tiene acceso directo al core. Hermes entra por el puente, no salta el muro.

---

## 6. Riesgos de Implementación

- **Contaminar el Core:** El mayor riesgo es introducir lógica de un dominio específico (ej. PyME) en el core, rompiendo el principio de separación y anulando la escalabilidad a otros dominios.
- **Diagnóstico Prematuro:** Que el sistema afirme una patología sin haber completado el ciclo de investigación y validación de evidencia.
- **Catálogo Académico Inútil:** Crear catálogos que no reflejen la realidad operativa, el lenguaje y los dolores de la PyME real.
- **Exceso de Abstracción:** Crear una arquitectura tan genérica que se vuelva imposible de implementar de forma concreta y útil.
