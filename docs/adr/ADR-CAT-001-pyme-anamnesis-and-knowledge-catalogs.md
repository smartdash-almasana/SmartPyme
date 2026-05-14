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

## Taxonomía inicial

La primera conversación debe clasificar al cliente en dimensiones operacionales.

Ejemplo:

```json
{
  "empresa_tipo": "fabrica | comercio | servicios | mixta",
  "industria": "textil | gastronomia | metalurgica | logistica | retail | otra",
  "canales_venta": ["local", "mercado_libre", "revendedores", "mayorista", "ecommerce"],
  "areas_criticas": ["stock", "caja", "produccion", "ventas", "precios", "compras", "sueldos"],
  "dolores_declarados": [],
  "documentos_disponibles": [],
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

### 7. Best Practices Catalog

Define prácticas recomendadas por rubro o función:

- revisar precios periódicamente
- conciliar cobros
- separar costos fijos y variables
- reponer antes de quiebre
- controlar margen por producto
- medir productividad por línea

### 8. Workflow Catalog

Define recetas de acción ante señales:

- alertar
- pedir evidencia
- recalcular
- sugerir acción
- pedir confirmación humana
- disparar capability
- bloquear ejecución

### 9. Industry Catalog

Define conocimiento por industria:

- textil
- comercio minorista
- fábrica
- gastronomía
- servicios
- logística
- metalúrgica

## Laboratorio inicial SmartPyme

Toda empresa nueva debe pasar por un primer laboratorio.

Flujo esperado:

```text
anamnesis
→ selección de catálogos
→ carga de evidencia
→ curación documental
→ entidades iniciales
→ fórmulas base
→ señales iniciales
→ mapa de faltantes
→ primer informe operativo
```

## Output del laboratorio inicial

El laboratorio debe devolver:

- qué datos hay
- qué datos faltan
- qué señales aparecen
- qué dolores declarados tienen evidencia
- qué riesgos son visibles
- qué áreas requieren más documentación
- qué capabilities conviene activar primero
- qué decisiones del dueño pueden destrabar análisis

## Relación con IA

La IA puede participar en:

- interpretar la anamnesis
- clasificar el rubro
- sugerir catálogos
- detectar faltantes
- priorizar preguntas
- explicar resultados
- proponer hipótesis

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

### Riesgos

- anamnesis demasiado larga
- clasificación incorrecta del rubro
- activación excesiva de catálogos
- pedir demasiada evidencia al inicio
- confundir dolor declarado con hecho validado

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

Estas decisiones deberán definirse en contratos técnicos posteriores.
