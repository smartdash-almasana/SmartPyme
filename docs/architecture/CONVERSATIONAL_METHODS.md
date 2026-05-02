# SmartPyme — Métodos conversacionales e investigativos

## Estado

Documento arquitectónico descartable para registro posterior en el repositorio.

Ruta sugerida en repo:

```text
docs/architecture/CONVERSATIONAL_METHODS.md
```

## Propósito

Este documento define la conversación como un componente mayor de SmartPyme y separa dos dimensiones metodológicas distintas:

1. La conversación interactiva con el dueño.
2. La conversación interna del sistema.

Ambas son necesarias, pero no cumplen la misma función.

---

## Principio central

SmartPyme trabaja con dos métodos complementarios:

```text
Mayéutica → hacia afuera, en la interacción con el dueño.
Método hipotético-deductivo → hacia adentro, en el procesamiento del sistema.
```

La mayéutica ayuda al dueño a formular con claridad.  
El método hipotético-deductivo ayuda al sistema a verificar con evidencia.

---

## Conversación como componente mayor

En SmartPyme, la conversación no es solamente una interfaz de chat. Es una capa operativa central.

La conversación permite:

- recibir la demanda del dueño;
- transformar dolor confuso en formulación clara;
- pedir evidencia sin invadir;
- registrar autorizaciones;
- sostener trazabilidad;
- producir decisiones documentadas;
- cerrar ciclos de diagnóstico, propuesta y acción.

La conversación es el medio por el cual el sistema transforma lenguaje humano en flujo operativo.

---

## Dos dimensiones de la conversación

| Dimensión | Interlocutores | Método | Finalidad |
|---|---|---|---|
| Conversación interactiva | Dueño ↔ SmartPyme | Mayéutica | Ayudar al dueño a formular con claridad y evidencia |
| Conversación interna | SmartPyme ↔ sus módulos | Hipotético-deductivo | Verificar hipótesis, deducir evidencia necesaria y producir diagnóstico |

---

## 1. Conversación interactiva con el dueño

### Método rector: mayéutica

La mayéutica es el método conversacional que SmartPyme utiliza con el dueño.

Su función no es imponer una verdad, sino ayudar a que el dueño formule mejor lo que está ocurriendo en su negocio.

El dueño muchas veces empieza con un dolor amplio:

```text
“Estoy perdiendo plata.”
“No me cierra la caja.”
“No sé si me falta stock.”
“Trabajo demasiado manual.”
“No sé si producir esto me conviene.”
```

Eso todavía no es un diagnóstico. Es una formulación inicial, humana, parcial y muchas veces confusa.

La tarea de SmartPyme es ordenar esa demanda mediante preguntas precisas.

---

## Mayéutica operativa

La mayéutica en SmartPyme significa:

```text
preguntar poco,
preguntar claro,
preguntar lo necesario,
preguntar con propósito.
```

No se trata de hacer un interrogatorio invasivo.  
Tampoco se trata de tener miedo de pedir información.

El sistema debe ser:

```text
no invasivo en el tono,
duro en las condiciones.
```

---

## Regla de interacción

Si falta información, SmartPyme no inventa.

Debe decir algo equivalente a:

```text
Para poder ayudarte con este reporte necesito esta información mínima.
Cuando la tengas, me lo mandás y seguimos.
```

El sistema espera. No fuerza. No diagnostica sin base.

---

## Ejemplo mayéutico: pérdida de margen

### Dolor inicial

```text
“Creo que estoy perdiendo plata.”
```

### Respuesta correcta del sistema

```text
Puede ser margen, stock, costos, descuentos o caja.
Para no adivinar, empecemos por una hipótesis concreta:
investigar si existe pérdida de margen.

Para verificarlo necesito:
1. ventas del período;
2. costos o facturas de proveedores;
3. productos o familias a revisar.

Con eso puedo confirmar, descartar o pedirte un dato adicional.
```

### Qué logra esta respuesta

- No afirma diagnóstico.
- Ordena el problema.
- Reduce ambigüedad.
- Explica por qué pide datos.
- Mantiene al dueño en control.
- Prepara el paso hacia el método interno.

---

## El dueño como fuente

En SmartPyme, el dueño es fuente de:

- demanda;
- contexto;
- documentación;
- evidencia;
- convalidación;
- autorización;
- decisión.

El sistema no debe tratar al dueño como obstáculo.  
Debe tratarlo como fuente primaria del caso.

Pero esa fuente debe ser ordenada, curada y validada.

---

## Preguntas duras, tono cuidado

SmartPyme debe poder decir:

```text
Con lo que me diste todavía no puedo armar un caso.
Necesito ventas, costos y período.
Cuando tengas esa información, seguimos.
```

Esto no es una falla del sistema.  
Es una protección de calidad.

Sin información suficiente:

```text
no hay OperationalCase;
no hay diagnóstico;
no hay reporte;
no hay acción.
```

---

## 2. Conversación interna del sistema

### Método rector: hipotético-deductivo

La conversación interna es el modo en que SmartPyme procesa la demanda una vez que fue formulada con suficiente claridad.

Acá ya no se trata de preguntarle al dueño, sino de razonar operativamente.

El sistema toma una demanda y la convierte en una hipótesis verificable.

---

## Secuencia interna

```text
Dolor expresado
→ síntoma operativo
→ patología posible
→ hipótesis investigable
→ variables necesarias
→ evidencia requerida
→ curación de datos
→ validación de condiciones
→ comparación/fórmula
→ diagnóstico
→ reporte
→ propuesta
→ nueva decisión del dueño
```

---

## Regla central del método interno

SmartPyme no arranca afirmando un problema.

Arranca formulando una hipótesis verificable.

```text
Mal:
“Hay pérdida de margen.”

Bien:
“Investigar si existe pérdida de margen por desalineación entre costos reales y precios de venta durante un período determinado.”
```

---

## Hipótesis, diagnóstico y hallazgo

Estos conceptos no deben mezclarse.

| Concepto | Qué significa |
|---|---|
| Dolor | Lo que el dueño expresa |
| Síntoma | Señal operativa interpretada |
| Patología posible | Patrón de daño que podría estar ocurriendo |
| Hipótesis | Formulación verificable |
| Diagnóstico | Resultado de contrastar evidencia |
| Hallazgo | Diferencia cuantificada, trazable y accionable |

---

## Ejemplo interno: pérdida de margen

### Dolor

```text
“Creo que estoy perdiendo plata.”
```

### Síntoma operativo

```text
Sospecha de pérdida de margen.
```

### Patologías posibles

```text
- desalineación costo-precio;
- costos de reposición desactualizados;
- descuentos no controlados;
- mix de productos deteriorado;
- impuestos o comisiones no incorporados;
- merma o pérdida de stock.
```

### Hipótesis

```text
Investigar si existe pérdida de margen por desalineación entre costos reales y precios de venta durante marzo.
```

### Deducción de evidencia requerida

Para verificar esa hipótesis se necesitan:

```text
- ventas reales;
- costos reales o facturas de proveedor;
- período;
- productos o familias;
- descuentos/promociones si aplican.
```

### Prueba

```text
Comparar precio real cobrado contra costo real o costo de reposición.
```

### Resultados posibles

```text
CONFIRMED
NOT_CONFIRMED
INSUFFICIENT_EVIDENCE
```

---

## Relación entre ambos métodos

La mayéutica prepara la demanda.  
El método hipotético-deductivo verifica la hipótesis.

```text
Mayéutica:
“¿Qué querés decir con perder plata?”
“¿Desde cuándo?”
“¿En qué productos?”
“¿Tenés ventas y costos?”

Hipotético-deductivo:
“Si la hipótesis es pérdida de margen, necesito comparar ventas contra costos.”
```

---

## Fórmula rectora

```text
La mayéutica ordena la demanda.
El método hipotético-deductivo ordena la investigación.
```

---

## Relación con componentes actuales

Este documento gobierna o influye sobre:

- AI Intake / Recepción;
- OwnerMessageInterpretation;
- Data Curation;
- Operational Conditions;
- ClarificationRequired;
- DecisionRecord;
- Job Authorization Gate;
- OperationalCase;
- DiagnosticReport;
- ValidatedCaseRecord;
- Atlas clínico-operativo de síntomas y patologías PyME;
- MCP Bridge;
- Hermes Runtime.

---

## Relación con ClarificationRequired

Cuando el sistema devuelve `CLARIFICATION_REQUIRED`, no debe ser un mensaje genérico.

Debe ser una intervención mayéutica.

Ejemplo incorrecto:

```text
Faltan datos.
```

Ejemplo correcto:

```text
Para investigar pérdida de margen necesito al menos ventas del período y costos o facturas de proveedor. Con eso puedo comparar precio real contra costo real. Cuando lo tengas, me lo mandás y seguimos.
```

---

## Relación con OperationalCase

El `OperationalCase` no se crea por cualquier conversación.

Solo se crea cuando existe material suficiente:

- demanda original usable;
- skill identificada;
- variables curadas o evidencia disponible;
- condiciones mínimas satisfechas.

Si falta contexto, el sistema devuelve la pelota al dueño:

```text
Necesito que me cuentes qué querés investigar o resolver para poder armar el caso.
```

---

## Relación con DiagnosticReport

El `DiagnosticReport` pertenece a la etapa interna del método hipotético-deductivo.

No puede confirmar diagnóstico sin:

- evidencia usada;
- comparación entre fuentes;
- diferencia cuantificada;
- fórmula o criterio aplicado;
- hallazgo trazable.

Regla:

```text
Sin evidencia trazable no hay diagnóstico confirmado.
Sin comparación entre fuentes no hay hallazgo fuerte.
Sin diferencia cuantificada no hay hallazgo accionable.
```

---

## Relación con DecisionRecord

Después de cada bifurcación importante, el dueño debe decidir.

La conversación mayéutica desemboca en decisiones registrables.

Ejemplos:

```text
INFORMAR
EJECUTAR
RECHAZAR
```

El `DecisionRecord` prueba:

- qué propuso el sistema;
- qué respondió el dueño;
- cuándo lo respondió;
- qué acción quedó autorizada o descartada.

Regla:

```text
Si no está registrado, no ocurrió.
```

---

## Relación con MCP Bridge

El MCP Bridge no decide.

Expone herramientas controladas para que Hermes Runtime interactúe con SmartPyme.

La conversación entra por herramientas, no por atajos.

Ejemplos:

```text
factory_process_intake
factory_record_decision
factory_start_authorized_job
factory_build_operational_case
```

---

## Relación con Hermes Runtime

Hermes Runtime puede orquestar, pero no debe saltear el método.

Debe respetar:

```text
mayéutica externa
→ hipótesis interna
→ evidencia
→ condiciones
→ decisión
→ acción controlada
```

Hermes no entra al core por la ventana.  
Hermes entra por MCP, con herramientas limitadas y contratos explícitos.

---

## Reglas semánticas rectoras

1. El dolor del dueño no es diagnóstico.
2. El síntoma no es patología confirmada.
3. La patología posible no es hallazgo.
4. El hallazgo requiere evidencia, comparación y diferencia cuantificada.
5. El sistema no pide datos porque sí.
6. Pide datos porque una hipótesis necesita variables y evidencia para ser verificada.
7. Si falta evidencia mínima, se pide aclaración.
8. No se crea OperationalCase sin material suficiente.
9. No se genera DiagnosticReport sin evidencia trazable.
10. No se ejecuta acción sin DecisionRecord.
11. La mayéutica ayuda al dueño a formular.
12. El método hipotético-deductivo ayuda al sistema a verificar.

---

## Conversación saludable

Una conversación saludable en SmartPyme debe:

- reducir ambigüedad;
- no abrumar;
- no inventar;
- pedir evidencia concreta;
- explicar para qué se pide;
- dejar al dueño en control;
- registrar decisiones;
- abrir el siguiente paso si corresponde.

---

## Cierre conceptual

SmartPyme no es solamente un software de automatización.

Es un sistema de conversación, investigación y decisión.

Su arquitectura metodológica se sostiene en dos movimientos:

```text
1. Hacia afuera:
   conversación mayéutica con el dueño.

2. Hacia adentro:
   procesamiento hipotético-deductivo del sistema.
```

La conversación hace aparecer la demanda.  
La investigación verifica la hipótesis.  
El reporte documenta.  
La propuesta orienta.  
El dueño decide.
