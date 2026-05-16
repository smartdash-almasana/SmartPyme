# ADR-CAP-001: Capability Runtime Contract

**Status:** Accepted

---

## Contexto

SmartPyme evoluciona desde un sistema de análisis documental y diagnóstico operacional hacia un runtime operacional PyME capaz de ejecutar múltiples capacidades sobre un núcleo matemático común.

La plataforma debe permitir incorporar nuevas capacidades sin alterar el kernel central ni romper contratos existentes.

---

## Decisión

Se establece el modelo de **Capability Runtime** como mecanismo oficial de extensión funcional de SmartPyme.

Una capability es una unidad operacional enchufable que declara explícitamente qué consume, qué produce, qué permisos requiere, qué acciones puede ejecutar y cómo deja trazabilidad.

Las capabilities no implementan su propio kernel. Reutilizan el núcleo común de SmartPyme.

---

## Núcleo compartido

Todas las capabilities deben apoyarse en:

- entidades canónicas
- evidencia curada
- contratos epistemológicos
- runtime conversacional
- trazabilidad
- sistema de permisos
- estados y tensiones
- observabilidad

---

## Contrato invariante de capability

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

---

## Principios arquitectónicos

### 1. Input/output cerrado

Cada capability debe poseer contratos explícitos de entrada y salida.

### 2. Trazabilidad obligatoria

Toda salida debe poder reconstruirse desde evidencia usada, fórmulas ejecutadas, señales detectadas, decisiones humanas y permisos aplicados.

### 3. Soberanía del dueño

Las capabilities no poseen autoridad absoluta. Pueden solicitar evidencia, solicitar clarificación, bloquear ejecución, requerir confirmación humana, proponer una acción o ejecutar una acción autorizada.

### 4. Extensión por catálogos

Las capabilities pueden cargar catálogos específicos por rubro, tenant o caso de uso: fórmulas, patologías, thresholds, buenas prácticas, workflows, reglas de negocio, políticas de autorización.

### 5. Separación determinístico / probabilístico

El núcleo matemático permanece determinístico.

Los componentes IA/probabilísticos pueden analizar, priorizar, sugerir, detectar patrones, redactar explicaciones y proponer hipótesis. Pero no pueden alterar hechos, estados confirmados ni decisiones operativas sin trazabilidad explícita y contrato válido.

---

## Ejemplos de capability

### Control de stock

- Input: productos, stock actual, ventas, compras, umbrales.
- Output: stock crítico, stock inmovilizado, productos sin rotación.
- Acciones: alertar, sugerir compra, sugerir liquidación.

### Proyección de caja

- Input: saldo bancario, cuentas por cobrar, cuentas por pagar, sueldos, impuestos, ventas proyectadas.
- Output: riesgo de caja, fecha estimada de quiebre, acciones posibles.
- Acciones: alertar, simular escenario, recomendar renegociación.

---

## Capability Registry

```text
capabilities/
  stock_control/
  cashflow_projection/
  mercado_libre_billing/
  bank_reconciliation/
```

Cada capability puede contener:

```text
manifest.json
contracts.py
service.py
rules/
catalogs/
tests/
```
