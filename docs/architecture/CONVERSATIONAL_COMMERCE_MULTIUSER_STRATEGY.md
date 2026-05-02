# SmartPyme — Comercio conversacional, microservicios y organización multiusuario

## Estado

Documento conceptual crítico de producto y arquitectura comercial.

Este documento consolida tres ideas conectadas:

1. SmartPyme puede vender y entregar microservicios puntuales desde el bot.
2. El bot puede funcionar como canal comercial conversacional.
3. Un mismo cliente/tenant puede tener múltiples usuarios internos interactuando con SmartPyme, con trazabilidad auditable para el dueño o responsable principal.

---

## Idea central

SmartPyme no es solamente un sistema que responde consultas.

Es una plataforma conversacional que puede:

```text
vender
recibir demanda
pedir evidencia
cobrar
entregar microservicios
abrir diagnósticos
registrar decisiones
operar sobre múltiples usuarios de una misma organización
generar trazabilidad para el dueño
```

---

# 1. Dos líneas de producto

SmartPyme tiene dos líneas comerciales que pueden convivir dentro de la misma arquitectura.

```text
1. Microservicios puntuales
2. Sistema operativo organizacional
```

---

## 1.1 Microservicios puntuales

Los microservicios son soluciones concretas, rápidas y comercializables de forma individual.

Ejemplos:

```text
- conciliación bancaria;
- liquidación de sueldos;
- limpieza de Excel;
- generación de plantilla Excel con fórmulas;
- macro para ordenar datos;
- cálculo BOM;
- cálculo de margen;
- comparación de proveedores;
- plantilla de costos;
- conversión de reportes;
- reparación de hojas de cálculo;
- generación de archivos descargables.
```

Estos servicios no siempre requieren todo el motor investigativo.

Pueden seguir un flujo simple:

```text
entrada simple
→ procesamiento
→ output descargable
```

Ejemplo:

```text
“Subime el Excel y te lo arreglo.”
```

O:

```text
“Te doy el link para descargar la plantilla que necesitás.”
```

---

## 1.2 Sistema operativo organizacional

El sistema operativo organizacional es el flujo completo:

```text
dolor
→ síntoma
→ hipótesis
→ evidencia
→ caso operativo
→ diagnóstico
→ reporte
→ propuesta
→ decisión
→ acción controlada
→ trazabilidad
```

Sirve para problemas complejos que requieren:

```text
- conversación mayéutica;
- evidencia;
- validación;
- condiciones;
- investigación;
- reportes;
- decisiones;
- autorización;
- seguimiento.
```

---

## Relación comercial entre ambas líneas

Los microservicios pueden ser la puerta de entrada.

```text
Microservicios para entrar.
Sistema operativo para quedarse.
Tanques de conocimiento para escalar por rubro.
```

Una persona puede entrar por algo pequeño:

```text
“Necesito una plantilla para costos.”
```

Y luego descubrir que SmartPyme también puede:

```text
- diagnosticar problemas de margen;
- revisar proveedores;
- detectar diferencias de stock;
- analizar caja/banco;
- ordenar procesos;
- generar reportes;
- acompañar decisiones.
```

---

# 2. Bot como canal comercial conversacional

El bot de Telegram o WhatsApp no es solo una interfaz de soporte.

Puede operar como:

```text
vendedor
recepcionista
mayéutico
cobrador
entregador de producto
orquestador inicial
canal de onboarding
canal de seguimiento
```

---

## Flujo comercial conversacional

Un posible flujo:

```text
vendedor humano consigue teléfono del dueño
→ se envía invitación al bot
→ el dueño empieza a hablar con SmartPyme
→ el bot escucha el problema
→ propone microservicio o diagnóstico
→ pide evidencia mínima
→ cobra si corresponde
→ entrega resultado o abre caso
→ registra decisión
→ ofrece siguiente paso
```

---

## Ejemplo comercial

Un vendedor visita un comercio y dice:

```text
“Dame tu teléfono y te mando el asistente.
Contale el problema directamente.
Si necesitás una plantilla, una conciliación o revisar un Excel, lo podés resolver ahí mismo.”
```

El cliente entra al bot y dice:

```text
“No me cierra el banco.”
```

El bot puede responder:

```text
“Puedo ayudarte con una conciliación bancaria simple.
Necesito extracto bancario, reporte de ventas/cobros y período a revisar.
Si querés, empezamos con un servicio puntual.”
```

Luego puede:

```text
- cobrar el microservicio;
- pedir archivos;
- entregar resultado;
- ofrecer diagnóstico más completo;
- derivar a suscripción.
```

---

## Bot vendedor, pero con límites

El bot puede vender y demostrar capacidad.

Pero debe respetar reglas:

```text
- no prometer resultados falsos;
- no diagnosticar sin evidencia;
- no ejecutar sin autorización;
- no ocultar condiciones;
- no inventar datos;
- no presionar al dueño;
- registrar decisiones importantes.
```

---

## Modelo de monetización

SmartPyme puede combinar:

```text
microservicios pagos
+ suscripción mensual
+ tanques por rubro
+ servicios avanzados
+ soporte humano opcional
```

Ejemplos:

```text
USD 5–15:
microservicio puntual, plantilla, macro, limpieza de archivo.

USD 25–30/mes:
PyME chica, uso básico, microdiagnósticos, plantillas, consultas.

USD 100–200/mes:
negocio con más flujo, reportes, seguimiento, múltiples usuarios.

Planes mayores:
fábricas, clínicas, cadenas, empresas con mayor complejidad.
```

---

## Bot como demostración de valor

El bot puede vender porque evidencia capacidad.

No necesita vender con discurso abstracto.

Puede mostrar:

```text
- “te arreglo este Excel”;
- “te preparo una plantilla”;
- “te explico cómo calcular tu margen”;
- “te digo qué datos faltan para investigar stock”;
- “te armo un primer diagnóstico si me das evidencia”.
```

Eso genera confianza.

---

# 3. Cliente/Tenant multiusuario

SmartPyme debe soportar que un mismo cliente tenga múltiples usuarios.

Ejemplo:

```text
cliente_id: metalurgica_ferroso
nombre: Metalúrgica Ferroso
```

Usuarios posibles:

```text
- dueño;
- contador;
- gerente comercial;
- gerente de compras;
- responsable de e-commerce;
- gerente de informática;
- encargado de producción;
- responsable de RRHH.
```

El tenant es uno:

```text
Metalúrgica Ferroso
```

Pero los usuarios son varios.

---

## Diferencia entre tenant y usuario

```text
Tenant / cliente:
la organización contratante.

Usuario:
persona autorizada dentro de esa organización.
```

Ejemplo:

```text
tenant:
Metalúrgica Ferroso

usuarios:
- juan_dueño
- maria_contadora
- pablo_compras
- lucia_ecommerce
- ricardo_it
```

---

## Implicancia arquitectónica

El sistema no debe identificar todo solo por `cliente_id`.

Debe poder distinguir:

```text
cliente_id
user_id
role
permissions
channel_id
conversation_id
```

Ejemplo conceptual:

```json
{
  "cliente_id": "metalurgica_ferroso",
  "user_id": "pablo_compras",
  "role": "compras",
  "channel": "telegram",
  "conversation_id": "conv_123"
}
```

---

## Roles posibles

Dentro de un mismo cliente puede haber roles:

```text
OWNER
ADMIN
MANAGER
ACCOUNTANT
PURCHASING
SALES
ECOMMERCE
IT
HR
OPERATIONS
VIEWER
```

Cada rol puede tener distintos permisos.

---

## Permisos

No todos los usuarios deben poder hacer lo mismo.

Ejemplo:

### Dueño

Puede:

```text
- ver todo;
- autorizar acciones;
- ver trazabilidad;
- consultar conversaciones de gerentes si la política de la empresa lo permite;
- pedir reportes globales;
- aprobar trabajos;
- configurar permisos.
```

### Contador

Puede:

```text
- subir documentación contable;
- pedir conciliaciones;
- revisar impuestos;
- trabajar sobre caja/banco;
- generar reportes contables.
```

### Gerente de compras

Puede:

```text
- cargar proveedores;
- pedir comparación de precios;
- subir facturas;
- revisar condiciones comerciales;
- detectar aumentos.
```

### Gerente comercial

Puede:

```text
- revisar ventas;
- consultar márgenes;
- analizar productos;
- pedir reportes comerciales.
```

### Responsable de e-commerce

Puede:

```text
- revisar catálogo;
- analizar ventas online;
- comparar precios;
- detectar desalineaciones.
```

### IT

Puede:

```text
- conectar sistemas;
- revisar integraciones;
- administrar tokens/API;
- habilitar fuentes.
```

---

## Dueño como observador estratégico

El dueño real puede pedir:

```text
“Mostrame qué estuvo trabajando cada gerente con SmartPyme esta semana.”
```

O:

```text
“Dame un reporte de trazabilidad de compras.”
```

O:

```text
“Qué decisiones autorizó el área comercial y qué resultados tuvieron.”
```

Esto transforma SmartPyme en una capa de gobierno organizacional.

---

## Trazabilidad por usuario

Cada interacción importante debe poder registrarse con:

```text
cliente_id
user_id
role
timestamp
canal
mensaje_original
propuesta_sistema
decision_record
job_id
case_id
report_id
resultado
```

Esto permite reconstruir:

```text
quién pidió qué
cuándo
con qué evidencia
qué decisión tomó
qué trabajo se abrió
qué reporte salió
qué acción se ejecutó
```

---

## Conversaciones auditables

El dueño podría consultar:

```text
- conversaciones del contador con SmartPyme;
- temas tratados por compras;
- pedidos del área comercial;
- evidencias subidas por e-commerce;
- decisiones tomadas por cada gerente;
- reportes generados por área.
```

Pero esto requiere reglas claras de privacidad y permisos internos.

---

## Regla de privacidad organizacional

Aunque el dueño contrate el sistema, no todo debe quedar expuesto sin política.

Debe definirse:

```text
- qué roles puede auditar el owner;
- qué conversaciones son visibles;
- qué datos son sensibles;
- qué requiere consentimiento interno;
- qué se registra por obligación operativa;
- qué se oculta o resume.
```

En empresas pequeñas, probablemente el dueño quiera visibilidad total.

En organizaciones más grandes, hay que soportar permisos más finos.

---

## Reportes de trazabilidad por área

SmartPyme podría generar reportes como:

```text
Reporte semanal de compras:
- temas consultados;
- proveedores analizados;
- facturas subidas;
- aumentos detectados;
- decisiones pendientes;
- trabajos abiertos;
- impacto estimado.
```

O:

```text
Reporte de área comercial:
- productos analizados;
- problemas de margen;
- descuentos revisados;
- reportes generados;
- decisiones sugeridas;
- oportunidades detectadas.
```

O:

```text
Reporte ejecutivo del dueño:
- actividad por área;
- decisiones tomadas;
- tareas pendientes;
- riesgos detectados;
- impacto económico estimado;
- usuarios más activos;
- cuellos de botella.
```

---

# 4. Multiusuario y DecisionRecord

El `DecisionRecord` actual registra decisiones del dueño o usuario autorizado.

En un sistema multiusuario, debería incluir o asociar:

```text
user_id
role
authorization_level
```

Porque no es lo mismo que confirme:

```text
- el dueño;
- el contador;
- el gerente de compras;
- un empleado sin permiso.
```

---

## Niveles de autorización

Ejemplo:

```text
LEVEL_0_VIEWER:
puede consultar información permitida.

LEVEL_1_OPERATOR:
puede pedir microservicios o reportes.

LEVEL_2_MANAGER:
puede abrir trabajos de su área.

LEVEL_3_OWNER:
puede autorizar acciones críticas, pagos, cambios y auditorías globales.
```

---

## Decisiones por rol

Algunas decisiones pueden ser válidas por rol.

Ejemplo:

```text
contador → puede autorizar conciliación bancaria;
compras → puede pedir comparación de proveedores;
comercial → puede pedir análisis de margen;
owner → debe autorizar acciones de alto impacto.
```

Regla:

```text
No toda decisión requiere al dueño,
pero toda decisión requiere un usuario autorizado para ese tipo de acción.
```

---

# 5. Multiusuario y microservicios

Los microservicios también pueden usarse por usuario.

Ejemplo:

```text
contador:
“Liquidame este archivo de sueldos.”

compras:
“Comparame estos proveedores.”

comercial:
“Arreglame esta lista de precios.”

e-commerce:
“Limpiame este catálogo.”

IT:
“Validame este CSV para importación.”
```

Cada microservicio puede generar:

```text
- registro de uso;
- archivo entregado;
- costo;
- usuario solicitante;
- área;
- resultado;
- posibilidad de upsell.
```

---

## Microservicios como entrada por área

Cada área puede empezar usando un microservicio puntual.

Después SmartPyme puede detectar patrones:

```text
El área de compras pide muchas comparaciones manuales.
El área comercial pide muchas correcciones de listas.
El contador pide muchas conciliaciones.
```

Eso puede derivar en propuesta:

```text
“Hay repetición de trabajo manual en estas áreas.
¿Querés que armemos un diagnóstico de automatización?”
```

---

# 6. Tenant multiusuario y tanques de conocimiento

Los tanques de conocimiento también pueden activarse por área.

Ejemplo Metalúrgica Ferroso:

```text
tenant:
Metalúrgica Ferroso

tanques activos:
- contabilidad
- finanzas
- compras
- proveedores
- producción industrial
- metalúrgica
- mantenimiento
- e-commerce
- recursos humanos
```

Usuarios:

```text
contador → usa contabilidad, impuestos, caja/banco
compras → usa proveedores, compras, metalúrgica
comercial → usa ventas, margen, clientes
e-commerce → usa catálogo, precios, stock
IT → usa integraciones, datos, automatización
owner → ve todo
```

---

## Beneficio estratégico

El sistema deja de ser un chatbot individual.

Se convierte en:

```text
una capa conversacional-operativa transversal a toda la organización
```

Cada usuario habla desde su área.

El sistema integra:

```text
conversaciones
evidecias
decisiones
casos
reportes
acciones
```

Por cliente.

---

# 7. Riesgos

## 7.1 Exceso de vigilancia

Riesgo:

```text
que el dueño use el sistema solo para vigilar empleados
```

Mitigación:

```text
enfocar trazabilidad en procesos, decisiones y evidencias,
no en control persecutorio.
```

---

## 7.2 Confusión de permisos

Riesgo:

```text
usuario sin autorización ejecuta o confirma acciones críticas
```

Mitigación:

```text
roles claros
permissions
authorization_level
DecisionRecord con user_id
AuthorizationGate por rol
```

---

## 7.3 Conversaciones privadas mezcladas con información operativa

Riesgo:

```text
el sistema almacena conversaciones sensibles sin política clara
```

Mitigación:

```text
política de visibilidad por organización
resumen auditado
redacción de datos sensibles
control por rol
```

---

## 7.4 Ruido organizacional

Riesgo:

```text
múltiples usuarios generen casos duplicados o contradictorios
```

Mitigación:

```text
case linking
deduplicación
áreas responsables
owner dashboard
```

---

# 8. Arquitectura futura sugerida

Componentes a considerar:

```text
Organization / Tenant
User
Role
Permission
ConversationRecord
DecisionRecord con user_id
MicroserviceUsageRecord
AreaTraceabilityReport
OwnerDashboard
```

---

## Entidades conceptuales

### Organization

```text
organization_id
name
domain_pack
enabled_knowledge_tanks
subscription_plan
billing_profile
```

### User

```text
user_id
organization_id
name
role
channel
permissions
is_active
```

### ConversationRecord

```text
conversation_id
organization_id
user_id
channel
started_at
last_activity_at
summary
topics
linked_jobs
linked_cases
linked_decisions
```

### MicroserviceUsageRecord

```text
usage_id
organization_id
user_id
microservice_id
input_files
output_files
price
status
timestamp
```

### AreaTraceabilityReport

```text
report_id
organization_id
area
period
users_included
topics
decisions
jobs
cases
impact
pending_actions
```

---

# 9. Producto comercial

Esto habilita una estrategia fuerte:

```text
vendedor humano
→ invitación al bot
→ bot vende microservicio
→ bot entrega valor rápido
→ bot detecta dolores más profundos
→ sistema propone diagnóstico
→ suscripción
→ múltiples usuarios
→ organización completa
```

---

## Planes posibles

### Plan microservicio

```text
pago por uso
sin suscripción
un usuario
output descargable
```

### Plan PyME básica

```text
suscripción baja
1–2 usuarios
microdiagnósticos
plantillas
historial básico
```

### Plan equipo

```text
varios usuarios
áreas
DecisionRecord
OperationalCase
reportes
trazabilidad
```

### Plan organización

```text
multiárea
owner dashboard
tanques configurables
reportes ejecutivos
integraciones
permisos avanzados
```

---

# 10. Frase estratégica

```text
El bot vende la primera solución.
Los microservicios demuestran valor.
La organización multiusuario retiene.
Los tanques de conocimiento escalan por industria.
```

---

# 11. Regla final

SmartPyme debe poder empezar como algo muy simple:

```text
“Subime el Excel y te lo arreglo.”
```

Y crecer hacia algo mucho más potente:

```text
“Dame trazabilidad de lo que compras, ventas, contabilidad y e-commerce estuvieron trabajando esta semana,
qué decisiones tomaron,
qué problemas aparecieron
y qué acciones conviene priorizar.”
```

Ese crecimiento no debe requerir cambiar el core.

Debe requerir:

```text
más usuarios
más permisos
más tanques
más evidencia
más reportes
más decisiones
```

---

## Próximos documentos o frentes sugeridos

1. `COMMERCIAL_CONVERSATIONAL_STRATEGY.md`
2. `MULTIUSER_TENANT_ARCHITECTURE.md`
3. `MICROSERVICES_PRODUCT_LAYER.md`
4. `KNOWLEDGE_TANKS_ARCHITECTURE.md`
5. `USER_ROLES_AND_PERMISSIONS.md`

---

## Cierre

La visión completa queda:

```text
Microservicios → adquisición
Bot conversacional → venta y entrega
Sistema operativo → retención
Multiusuario → organización completa
Tanques de conocimiento → expansión por industria
Trazabilidad → valor demostrable
```

Esto convierte a SmartPyme en una plataforma comercial, operativa y organizacional, no solamente en un asistente.