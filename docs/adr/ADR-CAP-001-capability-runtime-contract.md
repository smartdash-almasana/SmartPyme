# ADR-CAP-001: Capability Runtime Contract

**Status:** Accepted

## Contexto

SmartPyme evoluciona desde un sistema de análisis documental y diagnóstico operacional hacia un runtime operacional PyME capaz de ejecutar múltiples capacidades sobre un núcleo matemático común.

La plataforma debe permitir incorporar nuevas capacidades sin alterar el kernel central ni romper contratos existentes. Estas capacidades pueden cubrir, entre otras áreas:

- conciliación bancaria
- control de stock
- proyección de caja
- facturación Mercado Libre
- control de precios
- alertas operacionales
- workflows internos
- automatización administrativa
- diagnóstico operativo asistido

El sistema no debe crecer como un conjunto de features aisladas. Debe crecer como un ecosistema de capacidades interoperables, trazables y enchufables sobre una misma base operacional.

## Decisión

Se establece el modelo de **Capability Runtime** como mecanismo oficial de extensión funcional de SmartPyme.

Una capability es una unidad operacional enchufable que declara explícitamente qué consume, qué produce, qué permisos requiere, qué acciones puede ejecutar y cómo deja trazabilidad.

Las capabilities no implementan su propio kernel. Reutilizan el núcleo común de SmartPyme.

## Núcleo compartido

Todas las capabilities deben apoyarse en las piezas comunes del sistema:

- entidades canónicas
- evidencia curada
- contratos epistemológicos
- runtime conversacional
- trazabilidad
- jobs/workflows
- sistema de permisos
- estados y tensiones
- observabilidad

La capability puede tener lógica propia, pero no puede redefinir la semántica base del sistema.

## Contrato invariante de capability

Toda capability debe declarar un manifiesto estable. El contenido concreto puede variar, pero la forma contractual debe mantenerse.

Ejemplo de contrato base:

```json
{
  "capability_id": "string",
  "name": "string",
  "version": "string",
  "description": "string",

  "inputs": [],
  "outputs": [],

  "required_entities": [],
  "required_evidence": [],

  "supported_actions": [],

  "permissions": [],

  "risk_level": "LOW|MEDIUM|HIGH|CRITICAL",

  "requires_human_confirmation": true,

  "observability": {
    "logs": true,
    "metrics": true,
    "audit_trail": true
  }
}
```

## Principios arquitectónicos

### 1. Input/output cerrado

Cada capability debe poseer contratos explícitos de entrada y salida.

La implementación interna puede variar, pero la interfaz pública debe permanecer estable.

### 2. Trazabilidad obligatoria

Toda salida debe poder reconstruirse desde:

- evidencia usada
- fórmulas ejecutadas
- señales detectadas
- decisiones humanas
- workflows disparados
- permisos aplicados

### 3. Soberanía del dueño

Las capabilities no poseen autoridad absoluta.

Una capability puede:

- solicitar evidencia
- solicitar clarificación
- bloquear ejecución
- requerir confirmación humana
- proponer una acción
- ejecutar una acción autorizada

### 4. Extensión por catálogos

Las capabilities pueden cargar catálogos específicos por rubro, tenant o caso de uso:

- fórmulas
- patologías
- thresholds
- buenas prácticas
- workflows
- reglas de negocio
- políticas de autorización

Estos catálogos amplían el comportamiento de la capability sin modificar el kernel.

### 5. Separación determinístico / probabilístico

El núcleo matemático permanece determinístico.

Los componentes IA/probabilísticos pueden:

- analizar
- priorizar
- sugerir
- detectar patrones
- redactar explicaciones
- proponer hipótesis

Pero no pueden alterar hechos, estados confirmados ni decisiones operativas sin trazabilidad explícita y contrato válido.

## Capability Registry

SmartPyme debe evolucionar hacia un registro central de capabilities.

Estructura esperada:

```text
capabilities/
  stock_control/
  cashflow_projection/
  mercado_libre_billing/
  bank_reconciliation/
```

Cada capability podrá contener:

```text
manifest.json
contracts.py
service.py
rules/
catalogs/
tests/
```

## Ejemplos de capability

### Control de stock

- Input: productos, stock actual, ventas, compras, umbrales.
- Output: stock crítico, stock inmovilizado, productos sin rotación.
- Acciones: alertar, sugerir compra, sugerir liquidación, bloquear venta si falta stock.

### Facturación Mercado Libre

- Input: ventas Mercado Libre, reglas fiscales, datos del cliente, credenciales autorizadas.
- Output: facturas emitidas, errores, conciliación contra ventas y cobros.
- Acciones: emitir factura, marcar pendiente, pedir confirmación humana.

### Proyección de caja

- Input: saldo bancario, cuentas por cobrar, cuentas por pagar, sueldos, impuestos, ventas proyectadas.
- Output: riesgo de caja, fecha estimada de quiebre, acciones posibles.
- Acciones: alertar, simular escenario, recomendar renegociación o priorización de pagos.

## Consecuencias

### Positivas

- crecimiento modular
- extensibilidad fuerte
- aislamiento funcional
- reutilización del núcleo
- escalabilidad por dominio
- capacidades enchufables
- reducción de duplicación estructural
- mayor trazabilidad de acciones

### Riesgos

- explosión de catálogos
- duplicación de reglas entre capabilities
- capabilities superpuestas
- deriva semántica
- workflows contradictorios
- exceso de automatización sin autorización suficiente

Estos riesgos deben mitigarse con registry, versionado, tests, permisos y auditoría de ejecución.

## No decisiones

Este ADR no define todavía:

- implementación final del registry
- marketplace de capabilities
- formato definitivo de todos los catálogos
- scheduler distribuido
- runtime multi-tenant final
- política completa de publicación/versionado de capabilities
- UI de administración de capabilities

Estas decisiones deberán definirse en ADRs posteriores o contratos técnicos específicos.
