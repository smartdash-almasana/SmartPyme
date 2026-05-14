# ADR-CAT-001: PyME Anamnesis and Knowledge Catalogs

**Status:** Accepted

## Contexto

SmartPyme necesita activar su análisis a partir de una primera comprensión operacional de cada empresa.

Esa comprensión no debe depender de una conversación libre sin estructura. Debe existir una fase inicial de **anamnesis PyME** que permita identificar:

- qué tipo de empresa es
- qué rubro opera
- qué canales usa
- qué documentos puede aportar
- qué dolores declara el dueño
- qué áreas están bajo tensión
- qué capacidades iniciales conviene activar
- qué catálogos de conocimiento deben cargarse desde el comienzo

La anamnesis no reemplaza evidencia. Sirve para orientar la primera demanda de información y activar el laboratorio inicial.

## Decisión

Se establece la fase de **Anamnesis PyME** como patrón obligatorio para todo nuevo cliente.

Esta fase inicial debe producir una taxonomía operacional mínima y una selección explícita de catálogos de conocimiento.

El resultado de la anamnesis alimenta el primer **Laboratorio SmartPyme**, que será el análisis inicial de la empresa.

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

## Relación con BEM

BEM no recibe documentos sueltos sin contexto.

El sistema debe asociar cada documento a:

- tenant_id
- primer contrato de laboratorio
- hipótesis o dolor que se busca contrastar
- tipo documental esperado
- campos mínimos esperados
- workflow o función BEM adecuada
- criterio de suficiencia de evidencia

BEM reduce entropía documental. SmartPyme conserva la verdad operacional.

La salida de BEM no se acepta automáticamente como verdad. Debe validarse contra el contrato del laboratorio inicial.

## Objetivo de la Anamnesis

La anamnesis debe responder:

- qué empresa estamos mirando
- cómo vende
- cómo produce o presta servicio
- cómo cobra
- cómo paga
- qué documentos existen
- qué dolores reconoce el dueño
- qué áreas tienen prioridad
- qué datos faltan
- qué catálogos deben activarse
- qué primer informe se puede prometer con evidencia razonable

## Taxonomía inicial

La primera conversación debe clasificar al cliente en dimensiones operacionales.

Ejemplo:

```json
{
  "empresa_tipo": "fabrica | comercio | servicios | mixta",
  "industria": "textil | gastronomia | metalurgica | logistica | retail | otra",
  "modelo_comercial": "b2b | b2c | marketplace | mixto | desconocido",
  "canales_venta": ["local", "mercado_libre", "revendedores", "mayorista", "ecommerce"],
  "areas_criticas": ["stock", "caja", "produccion", "ventas", "precios", "compras", "sueldos", "impuestos", "tiempo", "automatizacion"],
  "dolores_declarados": [],
  "hipotesis_duenio": [],
  "frases_textuales": [],
  "documentos_disponibles": [],
  "documentos_solicitados": [],
  "capabilities_iniciales": [],
  "catalogos_activados": []
}
```

## Catálogos de conocimiento

SmartPyme debe operar con catálogos versionados.

Estos catálogos no son features aisladas. Son conocimiento estructurado que el runtime puede cargar, validar y aplicar sobre datos reales.

Catálogos mínimos:

```text
catalogs/
  taxonomy/
  entities/
  actions/
  formulas/
  signals/
  pathologies/
  pains/
  document_types/
  expected_fields/
  best_practices/
  workflows/
  industries/
```

## Tipos de catálogo

### 1. Taxonomy Catalog

Define rubros, tipos de empresa, canales, áreas y clasificaciones operacionales.

### 2. Entity Catalog

Define entidades PyME reutilizables:

- producto
- proveedor
- cliente
- empleado
- máquina
- cuenta bancaria
- deuda
- documento
- pedido
- factura

### 3. Action Catalog

Define acciones empresariales:

- comprar
- vender
- producir
- facturar
- pagar
- cobrar
- entregar
- reponer
- liquidar
- renegociar
- automatizar

### 4. Formula Catalog

Define fórmulas estándar PyME:

- margen
- rotación
- caja proyectada
- punto de equilibrio
- costo unitario
- productividad
- stock valorizado
- atraso de precios

### 5. Signal Catalog

Define señales detectables:

- ventas cero
- stock crítico
- stock inmovilizado
- margen negativo
- precio desactualizado
- caja insuficiente
- compras creciendo más que ventas
- devoluciones altas

### 6. Pathology Catalog

Define patologías operacionales:

- no rotación comercial
- fuga de margen
- sobrestock
- cuello de botella productivo
- desorden financiero
- precios atrasados
- riesgo de caja
- riesgo de continuidad
- improductividad operativa
- dependencia manual excesiva

### 7. Pain Catalog

Define dolores frecuentes expresados en lenguaje del dueño:

- no sé si gano
- vendo pero no me queda plata
- tengo mucho stock parado
- pierdo tiempo cargando planillas
- no sé qué producto me conviene vender
- no sé cuánto me cuesta producir
- no puedo controlar caja
- no sé si Mercado Libre me deja margen
- quiero ordenar el negocio

Estos dolores deben mapearse a patologías, señales, documentos requeridos y capabilities.

### 8. Document Type Catalog

Define tipos documentales esperables:

- lista de precios
- hoja de stock
- ventas
- compras
- cierre de caja
- factura
- remito
- extracto bancario
- reporte de marketplace
- planilla de producción
- planilla de sueldos
- captura informal

### 9. Expected Fields Catalog

Define campos mínimos esperados por tipo documental y capability.

Ejemplo para precios/márgenes:

```text
- producto
- precio_venta
- costo_unitario
- cantidad
- fecha
- fuente
```

### 10. Best Practices Catalog

Define prácticas recomendadas por rubro o función:

- revisar precios periódicamente
- conciliar cobros
- separar costos fijos y variables
- reponer antes de quiebre
- controlar margen por producto
- medir productividad por línea

### 11. Workflow Catalog

Define recetas de acción ante señales:

- alertar
- pedir evidencia
- recalcular
- sugerir acción
- pedir confirmación humana
- disparar capability
- bloquear ejecución
- pedir documentación adicional

### 12. Industry Catalog

Define conocimiento por industria:

- textil
- comercio minorista
- fábrica
- gastronomía
- servicios
- logística
- metalúrgica
- marketplace seller
- profesional independiente

## Laboratorio inicial SmartPyme

Toda empresa nueva debe pasar por un primer laboratorio.

Flujo esperado:

```text
anamnesis originaria
→ limpieza clínica conversacional
→ selección de catálogos
→ contrato de laboratorio inicial
→ pedido de documentación
→ carga de evidencia
→ curación documental
→ entidades iniciales
→ fórmulas base
→ señales iniciales
→ contraste contra dolores declarados
→ mapa de faltantes
→ informe de laboratorio de tu PyME
→ propuesta de siguiente contraste
```

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

## Relación con IA

La IA puede participar en:

- interpretar la anamnesis
- clasificar el rubro
- detectar frases con valor patológico
- sugerir catálogos
- detectar faltantes
- priorizar preguntas
- explicar resultados
- proponer hipótesis
- redactar síntesis para el dueño

Pero no puede afirmar datos operacionales sin evidencia real o cálculo del núcleo determinístico.

## Relación con capabilities

La anamnesis selecciona capabilities iniciales.

Ejemplo para una fábrica textil:

```text
- control_stock
- precios_y_margenes
- produccion_y_cuellos_de_botella
- mercado_libre_operacion
- caja_y_sueldos
- compras_y_materia_prima
```

Estas capabilities se activan según evidencia disponible, permisos y prioridades del dueño.

## Consecuencias

### Positivas

- evita onboarding desordenado
- reduce ambigüedad inicial
- activa catálogos correctos por empresa
- conecta dolores del dueño con evidencia
- permite construir diagnóstico inicial rápido
- prepara automatizaciones futuras
- habilita memoria genética operacional desde el primer contacto
- convierte el primer contacto en activo de datos
- permite vender continuidad desde evidencia, no desde promesa abstracta

### Riesgos

- anamnesis demasiado larga
- clasificación incorrecta del rubro
- activación excesiva de catálogos
- pedir demasiada evidencia al inicio
- confundir dolor declarado con hecho validado
- generar demanda sin evidencia suficiente
- convertir BEM en decisor operativo en vez de extractor documental

Estos riesgos deben mitigarse con preguntas mínimas, trazabilidad y demanda incremental de información.

## No decisiones

Este ADR no define todavía:

- formulario final de anamnesis
- UI de onboarding
- schema físico de los catálogos
- implementación del loader de catálogos
- ranking final de capabilities
- formato definitivo del informe inicial
- política comercial del laboratorio inicial
- modelo Pydantic definitivo de `AnamnesisOriginaria`
- modelo Pydantic definitivo de `LaboratorioInicialContrato`
- modelo Pydantic definitivo de `InformeLaboratorioPyME`
- persistencia final de memoria conversacional
- estrategia final Obsidian/RAG/vector store/memoria estructurada

Estas decisiones deberán definirse en contratos técnicos posteriores.
