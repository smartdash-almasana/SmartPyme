# Primer Tiempo Lógico — Historia Clínica Originaria

## Fuente

Extracto de ADR-CAT-001: PyME Anamnesis and Knowledge Catalogs

---

## Primer tiempo lógico: contacto originario

El primer contacto entre SmartPyme y una PyME debe tratarse como un **primer tiempo lógico**, no como una conversación genérica.

En este primer tiempo todavía no existe diagnóstico validado, historial operativo ni memoria consolidada. Existe una primera dialéctica entre el dueño o empleado de la PyME y el sistema.

Ese contacto originario debe producir dos efectos simultáneos:

```text
Cliente recibe:
→ una promesa concreta de valor: el primer informe de laboratorio de su PyME.

SmartPyme recibe:
→ la primera inscripción semántica y documental del caso.
```

El objetivo comercial y operacional de este primer intercambio es explícito:

```text
Entregar al cliente un primer reporte clínico-operacional de su negocio.
Construir para SmartPyme la primera memoria estructurada del caso.
```

---

## Primer contrato de intercambio

El primer contrato no es todavía una venta compleja ni una automatización profunda.

El contrato inicial es:

```text
El cliente aporta:
- relato de dolores, sufrimientos, dudas, hipótesis o deseos de mejora
- primera documentación disponible
- contexto mínimo sobre su operación

SmartPyme devuelve:
- primer informe de laboratorio de la PyME
- contraste inicial entre lo declarado y lo documentado
- primeros hallazgos accionables
- mapa de faltantes
- propuesta de próximos contrastes
```

Este contrato debe quedar registrado como dato estructurado. No debe perderse como conversación efímera.

---

## Captura semántica originaria

La anamnesis debe capturar texto o audio del dueño y transformarlo en registro clínico-operacional.

Debe conservar:

- frases textuales del dueño
- dolores declarados
- hipótesis propias del dueño
- certezas
- dudas
- áreas mencionadas
- indicadores semánticos de patología PyME
- deseos de mejora
- expectativas explícitas

Ejemplos de entrada semántica:

```text
vendo pero no sé si gano
creo que tengo mucho stock parado
me va bien pero quiero entender mejor el negocio
pierdo tiempo haciendo todo a mano
no sé si mis empleados rinden
no sé cuánto me queda limpio
quiero vender más por Mercado Libre
```

Estas frases no son todavía hechos. Son material clínico-operacional para contrastar.

---

## Limpieza clínica conversacional

Después de capturar la primera narración, el sistema debe devolver una síntesis al dueño.

Ejemplo de respuesta esperada:

```text
Esto entendí que querés revisar:
1. No sabés con claridad si ganás por producto.
2. Te preocupa tener stock inmovilizado.
3. Querés entender mejor el negocio antes de automatizar.
4. Sospechás que hay tareas que te consumen demasiado tiempo.

Para contrastar esto voy a necesitar documentación inicial.
```

Esta limpieza cumple tres funciones:

- valida que el sistema entendió al dueño
- transforma relato en objetos operacionales
- habilita el pedido de evidencia

---

## Pedido de documentación inicial

La documentación inicial no debe pedirse de forma genérica.

Debe pedirse como consecuencia del contrato de laboratorio y de las hipótesis declaradas.

Ejemplos:

```text
Si el dolor es margen:
→ lista de precios
→ costos unitarios
→ ventas recientes

Si el dolor es stock:
→ hoja de stock
→ movimientos
→ ventas por producto

Si el dolor es caja:
→ cierre de caja
→ extractos
→ cuentas por cobrar/pagar

Si el dolor es tiempo o tareas manuales:
→ descripción del proceso
→ planillas usadas
→ capturas del flujo de trabajo

Si el dolor es Mercado Libre:
→ export de publicaciones
→ ventas
→ costos/logística
```

El archivo puede llegar como Excel, PDF, imagen, captura, CSV, export de plataforma o texto estructurado.

---

## Recepción semántica y recepción matemática

El primer contacto produce dos clases de información:

### 1. Información semántica

Proviene de la conversación.

Incluye dolores, hipótesis, dudas, lenguaje del dueño, categorías operacionales y demanda explícita.

### 2. Información documental/computacional

Proviene de archivos o datos aportados.

Incluye planillas, PDFs, imágenes, capturas, exportaciones y registros transaccionales.

SmartPyme debe unir ambas fuentes:

```text
dolor declarado
→ documentación solicitada
→ evidencia curada
→ contraste
→ hallazgo o falta de evidencia
```

---

## Output del laboratorio inicial

El laboratorio debe devolver:

- qué datos hay
- qué datos faltan
- qué señales aparecen
- qué dolores declarados tienen evidencia
- qué dolores no pudieron contrastarse aún
- qué hipótesis del dueño se confirmaron parcialmente
- qué riesgos son visibles
- qué fortalezas aparecen
- qué áreas requieren más documentación
- qué capabilities conviene activar primero
- qué decisiones del dueño pueden destrabar análisis
- qué documentación adicional permitiría calcular nuevos indicadores

---

## Informe de laboratorio de tu PyME

El primer output vendible del sistema se denomina:

```text
Informe de laboratorio de tu PyME
```

Este informe debe ser concreto, limitado y accionable.

Debe incluir:

- resumen de la anamnesis originaria
- dolores declarados por el dueño
- documentación recibida
- evidencia que pudo curarse
- hallazgos confirmados
- hipótesis no confirmadas
- datos faltantes
- riesgos visibles
- fortalezas visibles
- próximos documentos sugeridos
- próxima pregunta operativa recomendada

Su función comercial es abrir demanda legítima:

```text
Con lo que aportaste puedo mostrarte esto.
Si aportás esta otra información, puedo calcular esto otro.
```

No debe prometer certeza donde solo hay indicios.
