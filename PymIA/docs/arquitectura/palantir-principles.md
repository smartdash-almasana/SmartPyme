# SmartPyme — Principios aprovechables de Palantir para ajuste de ingeniería

## Estado

Documento conceptual y arquitectónico.

## Tesis central

SmartPyme no debe copiar Palantir.

Debe extraer algunos principios de ingeniería:

```text
- ontología operativa
- objetos del negocio
- relaciones trazables
- acciones tipadas
- writeback de decisiones
- observabilidad
- separación entre semántica y cinética
- permisos por rol
- timeline de objetos/casos
```

Pero debe evitar:

```text
- complejidad enterprise prematura
- grafo gigante
- workflows visuales pesados
- permisos sobrediseñados
- plataforma corporativa difícil de operar
- despliegues caros
- abstracción excesiva antes del MVP
```

SmartPyme debe ser:

```text
Palantir mini,
conversacional,
PyME-first,
económico,
práctico,
orientado a diagnóstico y microservicios.
```

---

## Principios aprovechables

### 1. Ontología operativa

El sistema no debe guardar solo tablas o mensajes. Debe modelar objetos reales del negocio:

```text
Producto / Proveedor / Factura / Venta / Cuenta bancaria
Empleado / Usuario / Cliente / Orden de compra / Archivo
Evidencia / Caso operativo / Hallazgo / Decisión / Acción / Reporte
```

### 2. Separar semántica y cinética

```text
Semántica: qué cosas existen, qué significan y cómo se relacionan.
Cinética: qué acciones se pueden ejecutar sobre esas cosas.
```

Regla de ingeniería:

```text
Los tanques definen semántica.
Las skills investigan.
Las actions modifican o ejecutan.
El core coordina.
```

### 3. Links trazables entre objetos

```text
PRODUCT bought_from SUPPLIER
SALE contains PRODUCT
INVOICE evidences COST
FINDING affects PRODUCT
FINDING supported_by EVIDENCE
DECISION authorizes JOB
JOB creates OPERATIONAL_CASE
OPERATIONAL_CASE produces DIAGNOSTIC_REPORT
REPORT proposes ACTION
ACTION updates OBJECT
```

Esto permite reconstruir cadenas de verdad:

```text
dato → evidencia → caso → hallazgo → reporte → decisión → acción → impacto
```

### 4. Acciones tipadas

```text
AUTHORIZE_JOB
REQUEST_EVIDENCE
CREATE_OPERATIONAL_CASE
RUN_SKILL
GENERATE_DIAGNOSTIC_REPORT
VALIDATE_CASE
REGISTER_DECISION
REGISTER_ASSERTIVENESS
DELIVER_MICROSERVICE_OUTPUT
```

### 5. Writeback de decisiones

La decisión del usuario no debe quedar como conversación muerta. Debe volver al sistema como dato operativo.

```text
Toda decisión relevante vuelve al mapa operativo.
```

### 6. Timeline de objetos

Cada objeto importante debería tener historia.

Ejemplo producto "Leche Entera 1L":

```text
2026-03-01 → aparece en ventas
2026-03-05 → proveedor aumenta costo
2026-03-10 → se detecta margen bajo
2026-03-11 → se genera DiagnosticReport
2026-03-12 → dueño autoriza revisar precio
2026-03-13 → se actualiza matriz
2026-03-30 → se mide mejora
```

---

## Mínimo viable de inspiración Palantir

```text
OperationalObject
OperationalLink
ActionType
ActionRecord
CaseTimeline
```

Con eso alcanza para incorporar lo mejor sin sobrediseñar.

---

## Frase rectora

```text
No construir un bot que responde.
Construir una ontología operativa liviana donde cada conversación, evidencia, decisión y acción enriquece el mapa vivo de la organización.
```
