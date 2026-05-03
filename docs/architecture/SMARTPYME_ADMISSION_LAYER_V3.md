# SmartPyme — Arquitectura Semántica Conversacional V3

## Capa de Admisión, Anamnesis y Posicionamiento Inicial del Caso

**Versión:** 3.0  
**Fecha:** Mayo 2026  
**Estado:** Documento conceptual-operativo vigente para diseño de producto  
**Origen:** Sesiones de diseño, casos de uso en vivo y consolidación de arquitectura semántica conversacional  
**Uso:** Interno — Equipo de Producto SmartPyme

---

## 0. Propósito del documento

Este documento consolida la lógica de la primera capa de SmartPyme: la capa de admisión semántica, anamnesis operativa e inteligencia epistemológica.

Su objetivo no es implementar código todavía. Su objetivo es fijar una arquitectura conceptual clara para que luego pueda transformarse en contratos, catálogos, servicios, tests e interfaces.

La capa de admisión es crítica porque la primera conversación con el dueño define la calidad de todo lo que el sistema podrá hacer después.

Si la admisión lee mal, todo el sistema investiga mal.

---

## 1. Principio fundacional del sistema

SmartPyme no es un chatbot de respuestas rápidas.

SmartPyme es un sistema clínico-operativo de negocios que trabaja por ciclos, construye un caso con el dueño y nunca inventa hipótesis, datos ni diagnósticos.

### Principio rector

```text
El sistema no arranca con una demanda aislada.
Arranca con una anamnesis del negocio.
```

La secuencia invariable de la primera capa es:

```text
Dueño
→ Anamnesis
→ Taxonomía
→ Variables base
→ Demanda explícita
→ Demanda inferida controlada
→ Caso operativo inicial
```

La demanda del dueño no se toma como verdad técnica completa. Se toma como entrada humana inicial, situada en un negocio concreto, con información distribuida entre personas, documentos, memorias, sistemas, chats, planillas y desconocimientos.

---

## 2. Recuperar vs inventar

SmartPyme no inventa.

Todo lo que el sistema dice, pide, calcula o propone debe estar anclado en al menos una de estas fuentes:

1. una fórmula o método del Knowledge Tank;
2. un dato aportado o confirmado por el dueño;
3. una evidencia documental;
4. una patología identificada semánticamente en catálogo;
5. una referencia externa consultable por API/MCP cuando el conocimiento interno no alcance.

Si no hay fórmula + evidencia suficiente, el sistema no emite diagnóstico. Pide los datos que faltan, agenda tareas o limita el alcance.

### Forma incorrecta

```text
El sistema formula libremente una hipótesis.
```

### Forma correcta

```text
El sistema clasifica, recupera conocimiento, verifica evidencia, calcula y valida por ciclos con el dueño.
```

La hipótesis o el caso investigable no aparece de la nada. Surge de una cadena estructurada:

```text
Demanda del dueño
→ matching semántico
→ catálogo de síntomas / problemas / patologías
→ caso operativo candidato
→ Knowledge Tank
→ fórmula o método aplicable
→ evidencia requerida
→ tareas para obtener evidencia
→ ejecución determinística
→ resultado parcial
→ refrendo del dueño
```

---

## 3. ROI como árbitro universal

Todo el sistema está gobernado por ROI.

ROI no significa solamente retorno financiero. En SmartPyme incluye:

```text
ahorro de tiempo
ahorro de dinero
ganancia de dinero
dinero recuperado
riesgo reducido
fricción operativa eliminada
costo de obtener evidencia
costo de ejecutar una intervención
tiempo hasta valor
```

### Orden clínico de intervención

```text
1. Parar la sangría de dinero
2. Estabilizar el flujo operativo
3. Optimizar y escalar
```

Una empresa que quiere vender más mientras pierde dinero por mala ejecución, desorden documental, stock invisible o caja fragmentada suele fracasar más rápido: produce o vende más para compensar una pérdida que no entiende.

Por eso SmartPyme prioriza clínicamente:

```text
SANGRIA > INESTABILIDAD > OPTIMIZACION
```

---

## 4. Arquitectura de la capa de admisión

La primera conversación con el dueño es la más importante. En ella se construyen los cimientos del caso.

Ninguna investigación posterior puede funcionar bien sin una admisión bien ejecutada.

### Flujo de la primera fase

| Paso | Nombre | Qué hace el sistema |
|---|---|---|
| 1 | Recepción del planteo | Escucha el planteo inicial del dueño. No resuelve todavía. |
| 2 | Anamnesis operativa | Reconstruye contexto mínimo del negocio: rubro, operación, actores, fuentes, flujos. |
| 3 | Taxonomía | Clasifica qué tipo de empresa/comercio/fábrica/servicio es. |
| 4 | Variables base | Identifica variables transversales: caja, stock, ventas, compras, proveedores, personal, precios. |
| 5 | Análisis epistemológico | Clasifica cada bloque de información en CERTEZA / DUDA / DESCONOCIMIENTO. |
| 6 | Búsqueda semántica | Relaciona el planteo con síntomas, patologías y casos operativos candidatos. |
| 7 | Identificación de evidencia | Determina qué datos necesita, quién los tiene, en qué formato y cuándo estarán disponibles. |
| 8 | Mapa de fuentes | Registra responsables, documentos, chats, planillas, sistemas y accesibilidad. |
| 9 | Fase clínica | Decide si el foco inicial es SANGRIA, INESTABILIDAD u OPTIMIZACION. |
| 10 | Propuesta de fases | Propone etapas acotadas de trabajo y las cierra con el dueño antes de avanzar. |
| 11 | Iteración del dueño | El dueño valida, corrige, agrega o deriva. El caso se construye por capas. |

---

## 5. Inteligencia epistemológica

La inteligencia semántica sola no alcanza. SmartPyme necesita inteligencia epistemológica.

La inteligencia epistemológica responde:

```text
¿Qué se sabe?
¿Qué se duda?
¿Qué se ignora?
¿Quién tiene la información?
¿Dónde vive?
¿En qué formato está?
¿Cuándo estará disponible?
¿Qué tarea hace falta para obtenerla?
```

### Estados epistemológicos

| Estado | Definición | Señales del dueño | Acción del sistema |
|---|---|---|---|
| CERTEZA | Dato verificable, disponible o afirmado como existente. Puede tener confianza alta o baja. | “Tengo el Excel”, “Esta semana vendí $300.000”. | Activa el caso o habilita cálculo parcial. |
| DUDA | Información que puede existir pero no está disponible o confirmada ahora. | “Lo tiene Paulita”, “Le tengo que preguntar al contador”. | Registra responsable, formato, tiempo y tarea pendiente. |
| DESCONOCIMIENTO | Dato inexistente, nunca registrado o completamente ajeno al dueño. | “No tengo idea”, “Nunca hice eso”, “No sé qué es eso”. | No insiste. Lo deja fuera del alcance inicial salvo ROI suficiente. |

### Regla operativa

```text
CERTEZA → permite avanzar
DUDA → genera tarea
DESCONOCIMIENTO → se excluye temporalmente
```

La DUDA no se ignora. Se empuja hasta convertirse en:

```text
CERTEZA
DESCARTADO
REPLANIFICADO
```

---

## 6. La DUDA tiene dimensión temporal

La información también vive en el tiempo.

Una evidencia puede existir, pero no estar disponible ahora.

Ejemplos:

```text
“Ahora te mando el Excel.”
“La semana que viene vuelve Paulita de vacaciones.”
“El contador me lo da el mes que viene.”
“El reporte se cierra a fin de mes.”
```

Cada DUDA debe registrar:

```text
responsable
formato
tiempo estimado
motivo
acción de seguimiento
estado de tarea
```

### Reglas

```text
DUDA + fecha → tarea agendada
DUDA sin fecha → pedir fecha
DUDA vencida → insistir / replanificar / descartar
```

Ejemplo:

```text
EVIDENCIA: Excel_stock
ESTADO: DUDA
RESPONSABLE: Paulita
DISPONIBILIDAD: próxima semana
FOLLOW_UP: “Paulita ya volvió. ¿Le pediste el Excel?”
```

---

## 7. Plantel como mapa de acceso a datos

El dueño va nombrando personas en la conversación.

Cada persona puede ser un nodo de acceso a información.

No son personajes secundarios. Son parte del grafo operativo del caso.

Ejemplos:

```text
Paulita
contador
gerente
secretaria
abogado
encargado de depósito
responsable de ventas
empleado administrativo
proveedor
```

Cada persona puede tener:

```text
rol
información que gestiona
formato de esa información
disponibilidad
confiabilidad
canal de acceso
```

### Caso Perales

| Persona | Rol | Información que tiene | Formato |
|---|---|---|---|
| Paulita | Administración interna | Excel de stock, precios y ventas | Excel |
| Contador | Asesor externo | Gastos mensuales, parte blanca | PDF / Excel |
| Dueño | Fuente primaria | Ventas informales, caja negra, contexto | Input humano / WhatsApp |

---

## 8. Grafo de acceso a evidencia

La conversación debe convertirse en un grafo mínimo de acceso a evidencia.

### Entidades

```text
PERSONA:
  id
  nombre
  rol
  contacto opcional

FUENTE:
  id
  tipo
  formato
  owner_person_id
  ubicación

EVIDENCIA:
  id
  tipo
  source_id
  responsable_person_id
  estado epistemológico
  disponibilidad temporal
```

### Relaciones

```text
PERSONA --gestiona--> FUENTE
FUENTE --contiene--> EVIDENCIA
EVIDENCIA --habilita--> FORMULA
FORMULA --produce--> RESULTADO
RESULTADO --requiere--> VALIDACION_DUEÑO
```

### Ejemplo Perales

```text
Paulita --gestiona--> Excel_stock
Contador --gestiona--> Reporte_gastos
Dueño --gestiona--> WhatsApp_ventas
Excel_stock --contiene--> stock, precios, ventas
Reporte_gastos --contiene--> gastos_blancos
Excel_sueldos --contiene--> sueldos_blancos_y_negros
```

Esto transforma la conversación en logística de evidencia.

---

## 9. Sistema de activación del conocimiento

El sistema nunca genera hipótesis espontáneamente.

Para activar un cálculo, un diagnóstico o un caso operativo, sigue este ciclo:

| Fase | Descripción |
|---|---|
| Semántica de entrada | Lee el enunciado y extrae conceptos clave. |
| Búsqueda en catálogo de patologías | Relaciona conceptos con síntomas y patologías. |
| Caso operativo candidato | Selecciona un caso inicial posible. |
| Identificación de fórmula o método | Recupera fórmula/método del Knowledge Tank. |
| Solicitud de evidencia | Identifica datos requeridos y los pide si faltan. |
| Ejecución | Ejecuta solo con evidencia suficiente. |
| Reporte parcial | Muestra resultado operativo parcial. |
| Validación | El dueño valida, refuta, corrige o agrega. |
| Iteración | El sistema repite desde la capa correspondiente. |

### Regla crítica del ciclo

Cada ciclo se cierra con el dueño.

No se avanza al siguiente hasta que el dueño valida, refuta o reformula el resultado parcial.

El sistema trabaja por fases acotadas, no en modo “resolver todo”.

---

## 10. Catálogo de patologías vs Knowledge Tank

SmartPyme opera con capas de conocimiento diferenciadas.

### Catálogo de patologías

Sirve para:

```text
clasificar el problema
mapear síntomas
detectar patologías candidatas
activar casos operativos
```

No contiene toda la fórmula matemática ni todo el conocimiento técnico profundo.

### Knowledge Tank

Contiene:

```text
fórmulas
métodos
protocolos
modelos financieros
modelos de stock
modelos de caja
modelos de margen
modelos de proveedores
buenas prácticas
referencias externas
```

Puede ser interno o externo.

### Distinción clave

```text
Catálogo = estructura conceptual: qué buscar y cómo orientarse.
Datos = materia prima: con qué calcular.
Knowledge Tank = fórmulas y métodos: cómo calcular o fundamentar.
Caso operativo = puente que conecta demanda, patología, evidencia y fórmula.
```

---

## 11. Conocimiento interno y externo

El catálogo interno no puede ser infinito.

SmartPyme necesita combinar:

### Conocimiento interno

| Catálogo | Función |
|---|---|
| Taxonomía de negocio | Clasifica qué tipo de empresa es. |
| Catálogo de patologías PyME | Detecta desvíos, sangrías y problemas recurrentes. |
| Fórmulas operativas comunes | Cuantifican impacto en casos frecuentes. |
| Buenas prácticas | Orientan propuestas luego del diagnóstico. |

### Conocimiento externo

Para problemas específicos o variables cambiantes, el sistema puede consultar:

```text
APIs
MCPs
AFIP
INDEC
BCRA
precios de mercado
tipo de cambio
commodities
normativa fiscal
normativa laboral
catálogos académicos
universidades
instituciones sectoriales
```

### Regla

```text
El sistema usa conocimiento interno para arrancar rápido.
Consulta conocimiento externo cuando el caso lo requiere y el ROI lo justifica.
```

---

## 12. Caso de uso 1 — Textil Perales: stock desorganizado

### Demanda inicial

```text
Tengo entre 15.000 y 20.000 pantalones de jean azules.
No sé la cantidad exacta.
No sé los precios.
Los tengo desactualizados.
Paulita tiene un Excel por ahí.
Los vendo a revendedores.
Cuando viene un vendedor, le mando WhatsApp a Paulita para que lo anote en el Excel.
```

### Anamnesis mínima

```text
rubro: textil
producto: pantalones de jean azules
stock aproximado: 15.000–20.000
modelos: 4
talles: 5
organización física: por talle, color y modelo
canal de venta: revendedores
registro operativo: WhatsApp → Paulita → Excel
```

### Procesamiento epistemológico

| Información | Estado | Acción |
|---|---|---|
| Existen 15k–20k pantalones | CERTEZA | Activar caso de stock / capital inmovilizado. |
| Excel de Paulita | DUDA | Registrar responsable Paulita y tarea de solicitud. |
| Precios actualizados | DESCONOCIMIENTO / DUDA | Esperar Excel o lista alternativa. |
| Ventas por WhatsApp a Paulita | CERTEZA | Registrar canal de venta y fuente posible. |
| Organización por talle/color/modelo | CERTEZA | Usar como estructura base de conteo. |

### Síntomas detectados

```text
stock_desordenado
precios_desactualizados
registro_ventas_indirecto
control_operativo_fragil
informacion_fragmentada
```

### Patologías candidatas

```text
inventario_no_confiable
capital_inmovilizado_sin_rotacion
precios_no_gobernados
costo_reposicion_ignorado
venta_no_registrada
flujo_manual_con_intermediario
informacion_fragmentada
```

### Tareas pendientes

```text
TASK_001:
  responsable: dueño
  objetivo: pedir a Paulita el Excel de stock/precios
  formato esperado: .xlsx
  estado: PENDING

TASK_002:
  responsable: Paulita / dueño
  objetivo: confirmar si el Excel contiene modelo, talle, color, cantidad y precio
  estado: PENDING

TASK_003:
  responsable: dueño
  objetivo: reunir WhatsApps de ventas recientes a revendedores
  estado: PENDING
```

### Caso operativo inicial

```text
case_type: stock_price_control_admission
fase: INESTABILIDAD
objetivo: reconstruir base mínima de stock, precios y flujo de ventas
```

### ROI de intervención

Impacta en:

```text
capital inmovilizado
errores de venta
precios atrasados
pérdida de margen
tiempo administrativo
riesgo de venta no registrada
```

---

## 13. Caso de uso 2 — Textil Perales: caja blanca, caja negra y sangría

### Demanda inicial

```text
Tengo dos cajas.
Una en blanco que le mando al contador.
Ahí justifico gastos, materia prima y servicios.
Después pago una parte en negro a empleados.
Tengo una caja negra que no paga impuestos.
No sé en qué se me va la plata.
No me dan los números.
No sé cuánto tengo de stock.
No sé cuánto gasto.
No sé si puedo ahorrar.
No sé si me están robando.
No sé cómo entender mi negocio.
```

### Lectura clínica

Esta demanda activa fase:

```text
SANGRIA
```

El dueño no está pidiendo crecer. Está expresando pérdida de control económico.

### Síntomas detectados

```text
caja_fragmentada
gastos_no_consolidados
stock_no_cuantificado
resultado_real_desconocido
control_financiero_incompleto
imposibilidad_de_calcular_ganancia
riesgo_de_sangria_economica
```

### Patologías candidatas

```text
caja_partida_no_conciliada
costos_y_gastos_no_integrados
informalidad_operativa_no_modelada
resultado_real_no_calculable
sistema_financiero_fragmentado
dependencia_de_fuentes_externas
margen_invisible
flujo_caja_sin_anticipacion
```

### Procesamiento epistemológico

| Información | Estado | Acción |
|---|---|---|
| Ventas semana actual: 300.000 ARS | CERTEZA baja confianza | Usar como dato preliminar, pedir corroboración. |
| Ventas semana anterior: 250.000 ARS | CERTEZA baja confianza | Usar como dato preliminar, pedir corroboración. |
| Excel Paulita ventas | DUDA | Solicitar a Paulita. |
| Reporte contador gastos blancos | DUDA | Solicitar al contador. |
| Excel sueldos blanco + negro | DUDA | Solicitar al dueño. |
| Gastos totales reales | DESCONOCIMIENTO | Requiere integración documental. |
| Resultado real | DESCONOCIMIENTO | Requiere fórmula + evidencia. |

### Tareas pendientes

```text
TASK_001:
  responsable: dueño
  objetivo: pedir a Paulita Excel de ventas

TASK_002:
  responsable: dueño
  objetivo: pedir al contador reporte de gastos blancos del mes

TASK_003:
  responsable: dueño
  objetivo: subir Excel de sueldos blanco + negro

TASK_004:
  responsable: sistema
  objetivo: consolidar ingresos y egresos cuando llegue evidencia
```

### Fórmula básica recuperable del Knowledge Tank

```text
resultado_real = ingresos_reales - gastos_reales
```

Donde:

```text
ingresos_reales = ventas corroboradas
gastos_reales = gastos_blancos + gastos_informales + sueldos + otros egresos
```

### Output esperado del primer ciclo

```text
estado_de_caja_inicial
evidencia_faltante
riesgo_de_sangria
próxima acción recomendada
```

No es diagnóstico final.

---

## 14. Demanda explícita vs demanda inferida

La admisión debe separar dos planos.

### Demanda explícita

Lo que el dueño dice directamente.

Ejemplo:

```text
“No sé cuánto stock tengo.”
```

### Demanda inferida

Lo que el sistema detecta como posible derivación semántica.

Ejemplo:

```text
capital inmovilizado
precios desactualizados
pérdida de margen
ventas no registradas
flujo comercial frágil
```

### Regla

```text
La demanda inferida puede orientar el caso, pero no habilita acción sin validación del dueño.
```

El sistema puede decir:

```text
“Además del stock, esto podría estar afectando precios y margen. Primero ordenemos evidencia mínima. Después validamos si querés avanzar sobre margen.”
```

---

## 15. Investigación como proceso estructurado

La investigación no es narrativa.

Es un proceso completo que empieza con la demanda y termina en resultado parcial validado.

Incluye:

```text
armar caso
buscar conocimiento
pedir evidencia
crear tareas
esperar información
ejecutar fórmulas
devolver resultado
pedir refrendo
iterar
```

### Tipos de pasos estructurados futuros

```text
check_evidence
request_missing_evidence
schedule_follow_up
retrieve_formula
execute_formula
compare_sources
return_partial_result
ask_owner_validation
open_next_cycle
```

Estos pasos no deben ser texto libre. Deben convertirse en estructura ejecutable.

---

## 16. Capas del caso

El caso se construye por capas.

| Capa | Nombre | Contenido |
|---|---|---|
| 1 | Admisión y anamnesis | Demanda inicial, taxonomía, variables base, estados epistemológicos, mapa de fuentes. |
| 2 | Activación de conocimiento | Patologías detectadas, fórmulas asociadas, evidencia necesaria. |
| 3 | Recolección de evidencia | Documentos recibidos, fuentes confirmadas, tareas cerradas. |
| 4 | Cálculo y diagnóstico parcial | Fórmulas, resultados, comparación de fuentes, validación del dueño. |
| 5 | Nueva demanda / iteración | El dueño agrega o reformula; se repite desde la capa correspondiente. |
| 6 | Diagnóstico integral | Posición de la PyME, zonas de intervención, propuestas ordenadas por ROI. |

### Regla de iteración

El dueño no solo valida. Puede agregar semántica, corregir, aproximar o derivar hacia nuevos problemas en cualquier momento.

El sistema no cierra el caso unilateralmente.

---

## 17. Sistema de posicionamiento de la PyME

El resultado final de la fase diagnóstica no es una lista de problemas.

Es una coordenada en un sistema de referencia.

### Ejes

| Eje | Qué mide |
|---|---|
| Dinero | Ganancia, pérdida, eficiencia de capital, sangría. |
| Tiempo | Orden, caos, carga operativa, fricción. |

### Referencias

| Referencia | Pregunta |
|---|---|
| Taxonomía | ¿Qué es esta empresa? |
| Patologías | ¿Qué le pasa? ¿Dónde pierde dinero o tiempo? |
| Fórmulas | ¿Cuánto impacta? ¿Cuál es el número real? |
| Buenas prácticas | ¿Hacia dónde ir? ¿Qué cambiar primero? |

### Definición de diagnóstico

```text
El diagnóstico no es una lista.
Es una coordenada en un sistema de referencia:
nivel de salud operativa,
puntos de dolor activos,
y zonas de intervención priorizadas por ROI.
```

---

## 18. Contrato programático preliminar

Este contrato es preliminar y orientativo. No debe implementarse sin revisión técnica posterior.

```python
from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field

EpistemicState = Literal["CERTEZA", "DUDA", "DESCONOCIMIENTO"]
ClinicalPhase = Literal["SANGRIA", "INESTABILIDAD", "OPTIMIZACION"]
EvidenceAvailability = Literal["NOW", "SCHEDULED", "UNKNOWN"]
TaskStatus = Literal["PENDING", "DONE", "DISCARDED", "REPLANNED"]
Area = Literal["caja", "stock", "ventas", "admin", "produccion", "compras", "proveedores", "mixto"]

class Person(BaseModel):
    person_id: str
    name: str
    role: str
    contact: Optional[str] = None

class Source(BaseModel):
    source_id: str
    source_type: Literal["excel", "pdf", "whatsapp", "libreta", "sistema", "humano", "api", "mcp", "otro"]
    owner_person_id: Optional[str] = None
    location: Optional[str] = None
    notes: Optional[str] = None

class EvidenceItem(BaseModel):
    evidence_id: str
    evidence_type: str
    format: Optional[str] = None
    source_id: Optional[str] = None
    responsible_person_id: Optional[str] = None
    epistemic_state: EpistemicState
    confidence: float = Field(default=0.5, ge=0, le=1)
    availability: EvidenceAvailability = "UNKNOWN"
    earliest_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    notes: Optional[str] = None

class EvidenceTask(BaseModel):
    task_id: str
    task_type: Literal["REQUEST_EVIDENCE", "FOLLOW_UP", "CONFIRM_SOURCE", "REPLAN", "DISCARD_SCOPE"]
    evidence_id: str
    responsible_person_id: Optional[str] = None
    instruction: str
    due_date: Optional[datetime] = None
    status: TaskStatus = "PENDING"

class OwnerDemand(BaseModel):
    raw_text: str
    explicit_objective: str
    inferred_objectives: list[str] = []
    area: Area
    urgency: int = Field(default=3, ge=1, le=5)

class SymptomCandidate(BaseModel):
    symptom_id: str
    confidence: float = Field(ge=0, le=1)

class PathologyCandidate(BaseModel):
    pathology_id: str
    score: float = Field(ge=0, le=1)
    reason: Optional[str] = None

class InitialCaseAdmission(BaseModel):
    case_id: str
    cliente_id: str
    demand: OwnerDemand
    clinical_phase: ClinicalPhase
    people: list[Person] = []
    sources: list[Source] = []
    evidence: list[EvidenceItem] = []
    tasks: list[EvidenceTask] = []
    symptoms: list[SymptomCandidate] = []
    pathologies: list[PathologyCandidate] = []
    next_step: str
```

---

## 19. Metodología de documentación antes de código

Para evitar confusión conceptual, cada capa lógica debe documentarse antes de implementarse.

### Método

```text
caso humano
→ conversación dramatizada
→ extracción lógica
→ formalización conceptual
→ validación con otro caso
→ contrato programático preliminar
→ documentación en repo
→ implementación mínima
→ tests
```

### Reglas

```text
no escribir código sin lógica documentada
no crear contratos sin casos humanos
no crear catálogos sin ejemplos
no mezclar docs vigentes con docs obsoletas
```

### Auditoría documental futura

Cada documento del repo debe clasificarse como:

```text
KEEP
UPDATE
DEPRECATE
DELETE
```

Y debe incluir:

```text
estado
fecha
relación con capa lógica
si sigue vigente
si fue reemplazado
```

Esto evita acumulación caótica de conceptos viejos y nuevos sin fuente de verdad.

---

## 20. Flujo final consolidado

```text
Dueño habla
→ sistema hace anamnesis
→ clasifica taxonomía y variables base
→ extrae demanda explícita
→ detecta demandas inferidas controladas
→ identifica personas, fuentes y evidencias
→ clasifica evidencia en CERTEZA / DUDA / DESCONOCIMIENTO
→ asigna responsables y tiempos
→ detecta fase clínica: SANGRIA / INESTABILIDAD / OPTIMIZACION
→ matching semántico contra patologías
→ activa caso operativo inicial
→ consulta Knowledge Tank para fórmulas/métodos
→ pide paquete mínimo de evidencia
→ genera tareas pendientes
→ ejecuta solo con certeza suficiente
→ devuelve resultado parcial
→ dueño valida/corrige/agrega demanda
→ sistema itera
```

---

## 21. Principios rectores

- SmartPyme no inventa: clasifica, recupera, calcula y valida.
- El dueño es la primera fuente de conocimiento.
- La primera conversación es anamnesis, no soporte rápido.
- La demanda no se toma aislada: se ubica dentro de una taxonomía y variables base.
- La información tiene estado epistemológico.
- La información vive en personas, fuentes, formatos y tiempos.
- La DUDA no se ignora: se convierte en tarea.
- El DESCONOCIMIENTO se excluye salvo ROI suficiente.
- La admisión no resuelve: construye el caso.
- Primero se detiene la sangría, después se estabiliza, después se optimiza.
- Todo está gobernado por ROI.
- El catálogo clasifica patologías; el Knowledge Tank contiene fórmulas y métodos.
- La investigación es un proceso estructurado, no una narración.
- Cada ciclo debe cerrarse o refrendarse con el dueño.
- El diagnóstico final es una coordenada de salud operativa, no una lista suelta de problemas.

---

## 22. Próximos documentos y capas

1. Capa 2 — Metodología de investigación e iteración con fórmulas específicas.
2. Capa 3 — Búsqueda de conocimiento externo: cuándo y cómo activar APIs/MCP.
3. Capa 4 — Propuesta de optimización y automatización para la empresa.
4. Auditoría de documentación existente: contrastar docs vigentes, fusionar, actualizar y deprecar.

---

## 23. Alerta de mantenimiento

Los catálogos internos, especialmente fórmulas fiscales argentinas, alícuotas, multiplicadores de inflación, cargas sociales, índices y normativa, son ventaja competitiva y pasivo operativo simultáneamente.

Requieren actualización activa ante cada cambio normativo.

Esto no es contenido editorial. Es infraestructura de producto.
