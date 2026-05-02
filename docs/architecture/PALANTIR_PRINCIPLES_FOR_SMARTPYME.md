# SmartPyme — Principios aprovechables de Palantir para ajuste de ingeniería

## Estado

Documento conceptual y arquitectónico para incorporación posterior en el repositorio o continuidad de diseño.

Este documento responde a una pregunta concreta:

> ¿Qué puede tomar SmartPyme de Palantir/Foundry/Ontology sin copiar su escala enterprise ni desviarse del producto PyME-first?

La respuesta corta:

```text
Sí, estamos a tiempo de hacer este ajuste de ingeniería.
```

El ajuste no exige tirar lo construido.  
Exige ordenar mejor lo que ya venimos diseñando.

---

## Tesis central

SmartPyme no debe copiar Palantir.

Debe extraer algunos principios de ingeniería:

```text
- ontología operativa;
- objetos del negocio;
- relaciones trazables;
- acciones tipadas;
- writeback de decisiones;
- observabilidad;
- separación entre semántica y cinética;
- permisos por rol;
- timeline de objetos/casos.
```

Pero debe evitar:

```text
- complejidad enterprise prematura;
- grafo gigante;
- workflows visuales pesados;
- permisos sobrediseñados;
- plataforma corporativa difícil de operar;
- despliegues caros;
- abstracción excesiva antes del MVP.
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

# 1. Qué representa Palantir para nosotros

Palantir no es relevante porque “sea famoso”.

Es relevante porque resolvió una cuestión de ingeniería:

```text
cómo pasar de datos dispersos
a objetos operativos
a decisiones trazables
a acciones auditables.
```

SmartPyme está intentando resolver algo análogo, pero en otro mercado:

```text
PyMEs latinoamericanas,
negocios familiares,
comercios,
fábricas pequeñas,
distribuidoras,
gastronomía,
servicios,
organizaciones menos digitalizadas.
```

La diferencia es que SmartPyme debe operar con mucha menos estructura inicial.

Donde Palantir entra a corporaciones con grandes datasets, SmartPyme entra por:

```text
WhatsApp,
Telegram,
Excel,
PDF,
facturas,
fotos,
mensajes del dueño,
documentos sueltos,
dolores mal formulados.
```

---

# 2. Principio aprovechable 1: Ontología operativa

## Qué tomar

La idea de que el sistema no debe guardar solo tablas o mensajes.

Debe modelar objetos reales del negocio:

```text
Producto
Proveedor
Factura
Venta
Cuenta bancaria
Empleado
Usuario
Cliente
Orden de compra
Orden de producción
Archivo
Evidencia
Caso operativo
Hallazgo
Decisión
Acción
Reporte
```

Esto convierte el sistema en un mapa operativo vivo.

---

## Traducción a SmartPyme

En vez de que SmartPyme piense solo en:

```text
archivos,
jobs,
mensajes,
respuestas.
```

Debe poder pensar en:

```text
objetos operativos,
relaciones entre objetos,
evidecias que los respaldan,
acciones que los modifican,
decisiones que los autorizan.
```

Ejemplo:

```text
Producto “Leche Entera 1L”
→ comprado a Proveedor A
→ vendido en POS
→ asociado a Factura 123
→ afectado por Hallazgo de margen
→ incluido en DiagnosticReport
→ sujeto a Decisión de actualizar precio.
```

---

## Beneficio

Esto evita que el sistema sea una bolsa de scripts.

Permite:

```text
- memoria operacional;
- trazabilidad;
- navegación por entidad;
- reportes por objeto;
- historia por producto/proveedor/cliente/caso;
- medición de impacto.
```

---

# 3. Principio aprovechable 2: Separar semántica y cinética

## Qué significa

Una arquitectura sana distingue:

```text
Semántica:
qué cosas existen, qué significan y cómo se relacionan.

Cinética:
qué acciones se pueden ejecutar sobre esas cosas.
```

---

## En SmartPyme

### Semántica

```text
tanques de conocimiento
síntomas
patologías
evidencias
productos
proveedores
facturas
ventas
casos
hallazgos
decisiones
reportes
usuarios
roles
```

### Cinética

```text
pedir evidencia
registrar decisión
autorizar job
crear OperationalCase
ejecutar skill
generar DiagnosticReport
entregar microservicio
cobrar
registrar asertividad
cerrar caso
```

---

## Regla de ingeniería

```text
Los tanques definen semántica.
Las skills investigan.
Las actions modifican o ejecutan.
El core coordina.
```

Esta regla es clave.

Evita mezclar:

```text
qué sabe el sistema
```

con:

```text
qué hace el sistema.
```

---

# 4. Principio aprovechable 3: Objetos operativos

## Qué tomar

Crear una capa conceptual o técnica de objetos operativos.

No necesariamente un grafo enorme desde el inicio.

Pero sí una abstracción común:

```text
OperationalObject
```

---

## Contrato conceptual

```python
OperationalObject:
    object_id: str
    cliente_id: str
    object_type: str
    display_name: str
    properties: dict
    source_refs: list[str]
    created_at: str
    updated_at: str
```

---

## Ejemplos

```text
object_type: PRODUCT
object_type: SUPPLIER
object_type: INVOICE
object_type: SALE
object_type: BANK_ACCOUNT
object_type: EVIDENCE
object_type: OPERATIONAL_CASE
object_type: DIAGNOSTIC_REPORT
object_type: DECISION
object_type: ACTION
```

---

## Beneficio

Un hallazgo deja de ser texto suelto.

Pasa a estar vinculado a objetos:

```text
Hallazgo X afecta a Producto Y,
se sustenta en Factura Z,
se compara contra Venta W,
y deriva en Decisión D.
```

---

# 5. Principio aprovechable 4: Links trazables entre objetos

## Qué tomar

No basta con objetos. Hay que registrar relaciones.

```text
OperationalLink
```

---

## Contrato conceptual

```python
OperationalLink:
    link_id: str
    cliente_id: str
    from_object_id: str
    to_object_id: str
    link_type: str
    evidence_refs: list[str]
    created_at: str
```

---

## Ejemplos de links

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
USER belongs_to ORGANIZATION
USER performed ACTION
```

---

## Beneficio

Esto permite reconstruir cadenas de verdad:

```text
dato → evidencia → caso → hallazgo → reporte → decisión → acción → impacto
```

Y eso es exactamente lo que SmartPyme necesita para ser confiable.

---

# 6. Principio aprovechable 5: Acciones tipadas

## Qué tomar

Formalizar las acciones importantes como tipos explícitos.

No funciones sueltas.

```text
ActionType
```

---

## Ejemplos

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
APPROVE_PRICE_UPDATE
ARCHIVE_REPORT
```

---

## Contrato conceptual

```python
ActionType:
    action_type_id: str
    name: str
    required_role: str
    required_permissions: list[str]
    input_schema: dict
    preconditions: list[str]
    side_effects: list[str]
    audit_required: bool
```

---

## Beneficio

Cada acción importante declara:

```text
quién puede ejecutarla,
qué datos necesita,
qué condiciones exige,
qué efectos produce,
qué debe auditarse.
```

Esto reduce caos.

---

# 7. Principio aprovechable 6: ActionRecord

## Qué tomar

Cada ejecución concreta de una acción debe quedar registrada.

```text
ActionRecord
```

---

## Contrato conceptual

```python
ActionRecord:
    action_id: str
    cliente_id: str
    user_id: str
    role: str
    action_type_id: str
    inputs: dict
    status: str
    linked_job_id: str | None
    linked_case_id: str | None
    linked_report_id: str | None
    linked_decision_id: str | None
    timestamp: str
    result_summary: str
```

---

## Relación con lo ya construido

SmartPyme ya tiene piezas cercanas:

```text
DecisionRecord
JobAuthorizationService
JobExecutorService
OperationalCase
DiagnosticReport
ValidatedCaseRecord
MCP Bridge
```

El ajuste es:

```text
unificar acciones relevantes bajo ActionType/ActionRecord
```

sin reemplazar de golpe lo existente.

---

## Beneficio

Permite responder:

```text
quién hizo qué,
cuándo,
con qué permiso,
sobre qué caso,
con qué evidencia,
qué resultado produjo.
```

Esto alimenta directamente:

```text
Reporte de Asertividades Operativas
```

---

# 8. Principio aprovechable 7: Writeback de decisiones

## Qué tomar

La decisión del usuario no debe quedar como conversación muerta.

Debe volver al sistema como dato operativo.

---

## En SmartPyme

Cuando el dueño decide:

```text
“Sí, investigá margen.”
```

Eso debe producir:

```text
DecisionRecord
ActionRecord
Job autorizado
OperationalCase
```

Cuando el dueño autoriza:

```text
“Sí, actualizá la matriz de precios.”
```

Eso debe producir:

```text
DecisionRecord
ActionRecord
posible ejecución
registro de impacto
```

---

## Regla

```text
Toda decisión relevante vuelve al mapa operativo.
```

---

## Beneficio

SmartPyme aprende la historia operacional del cliente:

```text
qué se propuso,
qué se decidió,
qué se ejecutó,
qué impacto produjo.
```

---

# 9. Principio aprovechable 8: Timeline de objetos

## Qué tomar

Cada objeto importante debería tener historia.

```text
ObjectTimeline
```

---

## Ejemplo producto

Producto “Leche Entera 1L”:

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

## Contrato conceptual

```python
ObjectTimeline:
    object_id: str
    cliente_id: str
    events: list[ActionRecord]
```

---

## Beneficio

Permite mostrar evolución, no solo foto estática.

Eso es muy fuerte comercialmente:

```text
antes → después
problema → diagnóstico → acción → impacto
```

---

# 10. Principio aprovechable 9: Observabilidad de acciones

## Qué tomar

Cada acción importante debería poder medirse.

---

## Métricas mínimas

```text
cuántas veces se usó
quién la usó
cuántas fallaron
por qué fallaron
cuánto tardaron
qué casos habilitaron
qué reportes generaron
qué impacto produjeron
qué evidencia utilizaron
```

---

## Relación con Asertividades Operativas

Esto conecta directamente con:

```text
OperationalAssertivenessReport
```

Una asertividad puede generarse cuando una acción produjo valor:

```text
EVIDENCE_PROVIDED
CASE_ENABLED
DIAGNOSIS_ENABLED
DECISION_MADE
LOSS_DETECTED
SAVING_IDENTIFIED
REVENUE_OPTIMIZED
```

---

# 11. Principio aprovechable 10: Permisos por rol

## Qué tomar

No todos los usuarios pueden ejecutar todo.

---

## En SmartPyme multiusuario

Roles posibles:

```text
OWNER
ADMIN
ACCOUNTANT
PURCHASING
SALES
ECOMMERCE
IT
HR
OPERATIONS
VIEWER
```

---

## Regla

```text
No toda decisión requiere al dueño,
pero toda acción requiere un usuario autorizado para ese tipo de acción.
```

---

## Ejemplo

```text
contador → puede iniciar conciliación bancaria.
compras → puede pedir comparación de proveedores.
comercial → puede pedir análisis de margen.
owner → autoriza acciones de alto impacto.
```

---

## Beneficio

Permite que SmartPyme crezca de bot individual a capa operativa multiusuario.

---

# 12. Qué NO copiar de Palantir

## 12.1 No copiar escala enterprise

Palantir opera en escala corporativa, gubernamental e industrial grande.

SmartPyme debe entrar por:

```text
Excel
WhatsApp
Telegram
PDF
facturas
microservicios
dueño
equipo chico
```

No conviene diseñar primero para una corporación de 10.000 empleados.

---

## 12.2 No construir un grafo gigante al inicio

Riesgo:

```text
quedar atrapados armando infraestructura ontológica antes de entregar valor.
```

Mitigación:

```text
empezar con objetos y links mínimos.
```

Primero:

```text
Evidence
OperationalCase
DiagnosticReport
DecisionRecord
ActionRecord
Finding
```

Después:

```text
Product
Supplier
Invoice
Sale
BankAccount
Employee/User
```

---

## 12.3 No hacer un Ontology Manager visual pesado

No necesitamos inicialmente una interfaz visual compleja para editar ontologías.

Necesitamos:

```text
catálogos versionados
contratos simples
tests
documentación clara
registro auditable
```

---

## 12.4 No sobrediseñar permisos

Los permisos son necesarios, pero no conviene crear un sistema RBAC gigante al inicio.

V1 suficiente:

```text
OWNER
MANAGER
OPERATOR
VIEWER
```

Después se especializa.

---

## 12.5 No hacer workflows visuales prematuros

SmartPyme debe operar primero por conversación y MCP.

No necesitamos al inicio un constructor visual de procesos.

---

## 12.6 No perder foco PyME

El core puede ser general.

Pero el primer producto debe seguir siendo:

```text
SmartPyme V1
```

No saltar prematuramente a SmartClinic, SmartFactory, SmartBankOps, etc.

---

# 13. Ajuste de ingeniería recomendado

## Sí estamos a tiempo

Estamos a tiempo porque todavía estamos antes del bloque más pesado:

```text
OperationalCase → investigación técnica → DiagnosticReport real
```

Este es el momento correcto para introducir una capa ligera de:

```text
OperationalObject
OperationalLink
ActionType
ActionRecord
ObjectTimeline
```

---

## No hacerlo como gran reescritura

No conviene frenar todo para construir una ontología completa.

Conviene introducirlo incrementalmente.

---

# 14. Plan incremental

## Fase 1 — Documento y contratos conceptuales

Crear documentación:

```text
docs/architecture/PALANTIR_PRINCIPLES_FOR_SMARTPYME.md
```

Posibles contratos futuros:

```text
app/contracts/operational_object.py
app/contracts/action_record.py
```

---

## Fase 2 — ActionRecord mínimo

Antes que grafo completo, conviene empezar por acciones.

Porque ya tenemos:

```text
DecisionRecord
JobExecutorService
MCP Bridge
OperationalCase
```

Crear:

```text
ActionRecord
ActionType
```

Para registrar acciones relevantes.

---

## Fase 3 — Links mínimos

Agregar links entre:

```text
DecisionRecord → Job
Job → OperationalCase
OperationalCase → DiagnosticReport
DiagnosticReport → Evidence
Finding → Evidence
ActionRecord → DecisionRecord
```

---

## Fase 4 — Timeline de caso

Primero timeline por caso, no por todo objeto.

```text
CaseTimeline
```

Ejemplo:

```text
demanda recibida
evidenica solicitada
evidenica aportada
decisión registrada
job autorizado
caso creado
diagnóstico generado
acción propuesta
cierre validado
```

---

## Fase 5 — Objetos de negocio

Después agregar objetos específicos:

```text
Producto
Proveedor
Factura
Venta
Cuenta bancaria
Usuario
Área
```

---

# 15. Cómo se conecta con tanques de conocimiento

Los tanques definen semántica de dominio.

Ejemplo tanque_gastronomia:

```text
objetos:
- Plato
- Receta
- Ingrediente
- Merma
- Comanda

links:
- Plato usa Ingrediente
- Ingrediente comprado_a Proveedor
- Comanda vende Plato

acciones:
- calcular_food_cost
- detectar_merma
- revisar_precio_menu
```

Ejemplo tanque_metalurgica:

```text
objetos:
- Pieza
- Orden de producción
- Máquina
- Material
- BOM

links:
- Pieza requiere Material
- Orden produce Pieza
- Máquina procesa Orden

acciones:
- calcular_costo_orden
- detectar_cuello_botella
- revisar_merma_material
```

---

## Regla

```text
El core no conoce Plato ni Máquina.
El tanque los declara.
El core sabe registrar objetos, links, acciones y trazabilidad.
```

---

# 16. Cómo se conecta con microservicios

Un microservicio puntual también puede generar objetos, links y acciones.

Ejemplo:

```text
“Subime el Excel y te lo arreglo.”
```

Puede generar:

```text
ActionRecord: CLEAN_EXCEL
Evidence: archivo original
Output: archivo corregido
AssertivenessRecord: MICROSERVICE_VALUE_DELIVERED
Timeline event: archivo procesado
```

---

## Beneficio

Incluso un microservicio barato alimenta la memoria operacional.

No es una herramienta descartable.

---

# 17. Cómo se conecta con comercio conversacional

El bot puede decir:

```text
“Esta conciliación generó 3 diferencias documentadas y dejó 1 acción pendiente.”
```

Eso es posible si cada microservicio y cada decisión quedan como ActionRecord y links.

---

# 18. Cómo se conecta con Asertividades Operativas

El Reporte de Asertividades Operativas necesita trazabilidad.

Para medir una asertividad, el sistema debe saber:

```text
qué usuario aportó evidencia,
qué caso se pudo crear,
qué reporte salió,
qué decisión se tomó,
qué impacto se estimó.
```

Eso requiere:

```text
ActionRecord
OperationalLink
Timeline
```

---

# 19. Reglas de implementación sugeridas

1. No reemplazar lo existente.
2. Agregar capa de acciones de forma incremental.
3. No crear grafo complejo todavía.
4. Empezar con links entre registros ya existentes.
5. Mantener `cliente_id` obligatorio.
6. Agregar `user_id` cuando avance multiusuario.
7. Toda acción relevante debe ser auditable.
8. Toda acción debe tener estado.
9. Toda acción debe vincularse a objetos/casos/reportes cuando aplique.
10. Todo objeto o link debe poder apuntar a evidencia.

---

# 20. Mínimo viable de inspiración Palantir

El mínimo viable no es Foundry.

Es esto:

```text
OperationalObject
OperationalLink
ActionType
ActionRecord
CaseTimeline
```

Con eso alcanza para incorporar lo mejor sin sobrediseñar.

---

# 21. Riesgos de aplicar mal esta inspiración

## Riesgo 1: Parálisis por arquitectura

Querer diseñar todo el sistema ontológico antes del primer diagnóstico real.

Mitigación:

```text
solo objetos/acciones mínimos hasta tener DiagnosticReport real.
```

---

## Riesgo 2: Abstracción sin valor comercial

Crear objetos que nadie usa.

Mitigación:

```text
cada objeto debe servir a un reporte, caso, acción o asertividad.
```

---

## Riesgo 3: Contaminar el core con verticales

Mitigación:

```text
objetos sectoriales viven en tanques.
core solo entiende objetos genéricos y contratos.
```

---

## Riesgo 4: Duplicar registros existentes

Mitigación:

```text
ActionRecord complementa DecisionRecord, no lo reemplaza.
OperationalLink conecta registros, no los duplica.
```

---

# 22. Frase rectora

```text
No construir un bot que responde.
Construir una ontología operativa liviana donde cada conversación, evidencia, decisión y acción enriquece el mapa vivo de la organización.
```

Versión SmartPyme:

```text
menos enterprise,
más conversacional,
más PyME,
más barata,
más rápida,
más trazable,
más orientada a impacto.
```

---

# 23. Próximo documento / ruta sugerida

Ruta sugerida:

```text
docs/architecture/PALANTIR_PRINCIPLES_FOR_SMARTPYME.md
```

---

# 24. Próximo frente técnico sugerido

No saltar todavía a implementación pesada.

Secuencia recomendada:

```text
1. Registrar este documento.
2. Resolver provider Gemini/Vertex/ADC en Hermes.
3. Sincronizar docs pendientes.
4. Retomar TS_026C_SYMPTOM_PATHOLOGY_CATALOG.
5. Después evaluar TS_027_ACTION_RECORDS_AND_OPERATIONAL_LINKS.
```

---

# 25. Cierre

Sí: estamos a tiempo.

El ajuste de ingeniería es oportuno porque SmartPyme ya tiene:

```text
DecisionRecord
AuthorizationGate
JobExecutorService
OperationalCase
MCP Bridge
tanques de conocimiento
método mayéutico
método hipotético-deductivo
asertividades operativas
```

Lo que falta es una capa ligera que conecte todo como mapa operacional:

```text
objetos
links
acciones
timelines
observabilidad
```

Eso no cambia la visión.  
La fortalece.

SmartPyme debe seguir siendo PyME-first, conversacional y práctico.

Pero con una ingeniería más profunda:

```text
cada dato tiene fuente;
cada caso tiene historia;
cada hallazgo tiene evidencia;
cada decisión tiene autor;
cada acción tiene permiso;
cada impacto tiene trazabilidad.
```
