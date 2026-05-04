# SmartPyme — Capa 01: Admisión e Interpretación de Intención

## Estado

DOCUMENTO RECTOR — REESCRITO v2.0  
**Fecha:** Mayo 2026  
**Cambio principal v2:** Separación explícita de Capa 00 (canal/entrada cruda) y Capa 01 (interpretación de intención). Capa 01 ya no recibe entrada cruda directamente. Recibe `RawInboundEvent` de Capa 00. Aclaración obligatoria: fases clínicas, patologías, síntomas y semántica PyME viven en catálogos, Domain Packs o Knowledge Tanks — no en el core de Capa 01.

---

## Regla rectora

```text
Capa 01 interpreta intención inicial.
Capa 01 no diagnostica.
Capa 01 no propone acción.
Capa 01 no arma caso operativo.
Capa 01 ordena la demanda y la prepara para capas posteriores.
```

---

## 1. Posición en la arquitectura

```text
Canal externo
  ↓
Capa 00  → RawInboundEvent
  ↓
Capa 01  → InitialCaseAdmission + OwnerDemandCandidate  ← esta capa
  ↓
Capa 1.5 → NormalizedEvidencePackage
  ↓
Capa 02  → OperationalCaseCandidate
  ↓
Capa 03  → OperationalCase
```

Capa 01 recibe el `RawInboundEvent` de Capa 00 y lo transforma en una demanda interpretada.

No recibe entrada cruda directamente del canal.  
No produce diagnóstico.  
No produce caso operativo.

---

## 2. Principio fundamental

```text
Capa 01 lee la intención del dueño.
No la resuelve.
No la diagnostica.
La ordena y la prepara.
```

La primera interacción no está diseñada para resolver la demanda.  
Está diseñada para leer correctamente el enunciado del dueño, identificar su intención y preparar el caso inicial para las capas siguientes.

Frase rectora:

> Toda buena lectura del enunciado anuncia una mejor resolución del problema.

---

## 3. Qué entra a Capa 01

La entrada principal es:

```text
RawInboundEvent  (de Capa 00)
```

Puede venir acompañado de:

```text
conversation_history  historial de la conversación si existe
client_context        contexto del cliente si está disponible
```

Capa 01 no recibe archivos crudos directamente.  
Los archivos llegan como `RawInboundEvent` con `raw_content_type = file`.  
Capa 01 los registra como evidencia pendiente y los deriva a Capa 1.5.

---

## 4. Tipos de intención que Capa 01 distingue

Capa 01 clasifica la intención del dueño en uno de estos tipos:

### QUIERE_ENTENDER

El dueño expresa un dolor o confusión y quiere entender qué está pasando.

```text
"No sé cuánto stock tengo."
"No me dan los números."
"No entiendo por qué pierdo plata."
```

Acción de Capa 01: ordenar la demanda, identificar el dolor, formular aclaración mayéutica mínima.

### QUIERE_ACTUAR

El dueño quiere hacer algo concreto.

```text
"Quiero revisar el stock."
"Quiero calcular el margen."
"Quiero saber si me conviene producir esto."
```

Acción de Capa 01: registrar la intención de acción, identificar qué evidencia se necesita.

### QUIERE_SUBIR_EVIDENCIA

El dueño envía un archivo, imagen, audio o documento.

```text
[adjunta Excel de Paulita]
[adjunta foto de estantería]
[adjunta factura del proveedor]
```

Acción de Capa 01: registrar la evidencia como pendiente de normalización, derivar a Capa 1.5.

### QUIERE_AUTORIZAR

El dueño responde a una propuesta o solicitud del sistema.

```text
"Sí, adelante."
"Confirmado."
"Hacelo."
```

Acción de Capa 01: registrar la autorización como respuesta a una solicitud previa.

### QUIERE_CONSULTAR_ESTADO

El dueño pregunta por el estado de algo.

```text
"¿Cómo va el análisis?"
"¿Qué falta?"
"¿Ya tenés los resultados?"
```

Acción de Capa 01: registrar la consulta y derivar al estado del caso activo.

---

## 5. Qué hace Capa 01

Capa 01:

- recibe el `RawInboundEvent` de Capa 00;
- identifica el tipo de intención del dueño;
- ordena la demanda inicial;
- identifica el dolor expresado como dolor, no como diagnóstico;
- clasifica la información disponible según estado epistemológico (CERTEZA / DUDA / DESCONOCIMIENTO);
- registra personas, fuentes y evidencias mencionadas;
- genera tareas de evidencia pendientes;
- formula una aclaración mayéutica mínima si la demanda es ambigua;
- deriva evidencia cruda (archivos, imágenes, audios) hacia Capa 1.5;
- produce `InitialCaseAdmission` y `OwnerDemandCandidate`.

**Nota sobre semántica de dominio:**  
Las fases clínicas (SANGRIA, INESTABILIDAD, OPTIMIZACION), las patologías, los síntomas y la semántica PyME no viven en el core de Capa 01.  
Viven en catálogos, Domain Packs o Knowledge Tanks.  
Capa 01 puede mencionar candidatos conversacionales basados en el dolor expresado, pero no los hardcodea como contrato de core.

---

## 6. Qué NO hace Capa 01

Capa 01 no:

- recibe entrada cruda directamente del canal (eso es Capa 00);
- mapea evidencia en profundidad (eso es Capa 1.5);
- resuelve entidades, aliases o tiempo (eso es Capa 1.5);
- detecta fase clínica como hecho confirmado;
- confirma patologías;
- crea `OperationalCaseCandidate` (eso es Capa 02);
- genera diagnóstico;
- genera propuesta de acción;
- crea `DecisionRecord`;
- activa `AuthorizationGate`;
- ejecuta acciones;
- calcula fórmulas;
- produce `OperationalCase`.

---

## 7. Inteligencia epistemológica

La inteligencia epistemológica es el núcleo de Capa 01.

SmartPyme no trata toda la información como equivalente.  
Cada bloque de información aportado por el dueño se clasifica según su estado de conocimiento.

### CERTEZA

Información disponible, afirmada como existente o verificable.

```text
"Esta semana vendí 300.000 pesos."
```

Una certeza puede tener distintos niveles de confianza.  
Una cifra recordada por el dueño es certeza declarada, pero no evidencia documental fuerte.

```text
CERTEZA → permite avanzar, pero puede requerir corroboración.
```

### DUDA

Información que podría existir, pero no está disponible o confirmada.

```text
"Paulita tiene un Excel por ahí."
```

```text
DUDA → genera tarea.
```

Toda DUDA debe registrar:

- responsable;
- fuente probable;
- formato esperado;
- fecha o tiempo estimado;
- acción de seguimiento.

### DESCONOCIMIENTO

Información inexistente, inaccesible o desconocida por completo.

```text
"No tengo idea del stock real."
```

```text
DESCONOCIMIENTO → queda fuera del alcance inicial, salvo ROI suficiente.
```

### Regla epistemológica central

```text
CERTEZA → permite avanzar
DUDA → genera tarea
DESCONOCIMIENTO → se excluye salvo ROI suficiente
```

---

## 8. Mayéutica mínima

Cuando la demanda es ambigua, Capa 01 formula una aclaración mayéutica mínima.

La mayéutica en Capa 01 significa:

```text
preguntar poco,
preguntar claro,
preguntar lo necesario,
preguntar con propósito.
```

No es un interrogatorio.  
Es una pregunta precisa que reduce la ambigüedad sin invadir.

Ejemplo:

```text
Dueño: "No me dan los números."

Capa 01: "¿Qué área querés revisar primero: ventas, stock, caja o costos?"
```

Capa 01 no diagnostica con la respuesta.  
Registra la respuesta como parte de la demanda ordenada.

---

## 9. Registro de personas, fuentes y evidencias

La conversación del dueño revela una red organizacional.

Capa 01 registra:

```text
PERSONA:
  nombre o apodo
  rol operativo
  contacto opcional

FUENTE:
  tipo (Excel, PDF, WhatsApp, cuaderno, sistema)
  formato
  responsable
  ubicación

EVIDENCIA_PENDIENTE:
  tipo
  fuente
  responsable
  estado epistemológico
  acción requerida
```

Este registro es superficial.  
La resolución profunda de entidades, aliases y tiempo pertenece a Capa 1.5.

---

## 10. Derivación de evidencia cruda a Capa 1.5

Cuando el dueño sube un archivo, imagen o audio, Capa 01:

- registra la evidencia como pendiente;
- crea una tarea de normalización;
- deriva el `RawInboundEvent` correspondiente a Capa 1.5.

Capa 01 no procesa el contenido del archivo.  
No normaliza columnas.  
No resuelve entidades.  
Solo registra y deriva.

---

## 11. Outputs de Capa 01

Capa 01 produce dos objetos:

### InitialCaseAdmission

Consolida el entendimiento inicial del caso:

```text
InitialCaseAdmission:
  case_id               UUID único del caso de admisión
  cliente_id            tenant
  raw_event_id          ID del RawInboundEvent de origen
  demand                OwnerDemand (texto original + objetivo explícito)
  intent_type           QUIERE_ENTENDER | QUIERE_ACTUAR | QUIERE_SUBIR_EVIDENCIA |
                        QUIERE_AUTORIZAR | QUIERE_CONSULTAR_ESTADO
  clinical_phase_hint   candidato conversacional de fase clínica (no confirmado)
  people                personas identificadas
  sources               fuentes identificadas
  evidence              evidencias con estado epistemológico
  tasks                 tareas pendientes de evidencia
  symptoms_hint         síntomas candidatos conversacionales (no confirmados)
  pathologies_hint      patologías candidatas conversacionales (no confirmadas)
  next_step             próximo paso sugerido
```

**Nota:** `clinical_phase_hint`, `symptoms_hint` y `pathologies_hint` son candidatos conversacionales.  
No son hechos confirmados.  
No son contratos de core.  
Viven en catálogos y Domain Packs.  
Capa 02 los valida contra el Knowledge Tank activo.

### OwnerDemandCandidate

Representa la demanda del dueño como candidato interpretado:

```text
OwnerDemandCandidate:
  demand_id             UUID único de la demanda
  case_id               ID del InitialCaseAdmission
  raw_text              texto original del dueño, sin modificar
  explicit_objective    objetivo explícito extraído
  inferred_objectives   objetivos inferidos (no habilitan acción sin validación)
  intent_type           tipo de intención detectado
  area_hint             área operativa candidata (caja, stock, ventas, admin, produccion, mixto)
  urgency               urgencia percibida 1-5
  clarification_needed  si se necesita aclaración antes de avanzar
  clarification_question pregunta mayéutica si clarification_needed=true
```

---

## 12. Diferencia entre InitialCaseAdmission y OperationalCase

### InitialCaseAdmission (Capa 01)

Es el resultado de la primera interpretación.

Documenta:

- intención del dueño;
- dolor expresado;
- evidencia disponible y faltante;
- personas y fuentes identificadas;
- tareas pendientes;
- candidatos conversacionales de fase clínica y patologías.

Su propósito es preparar el caso para Capa 1.5 y Capa 02.

### OperationalCase (Capa 03)

Nace mucho después.

```text
InitialCaseAdmission (Capa 01)
  → NormalizedEvidencePackage (Capa 1.5)
  → OperationalCaseCandidate (Capa 02)
  → OperationalCase (Capa 03)
```

Solo se crea cuando hay evidencia suficiente, hipótesis formulada y validación del dueño.

---

## 13. Ejemplo — Perales: stock y precios

### Entrada (RawInboundEvent de Capa 00)

```text
channel: telegram
raw_content_type: text
raw_text: "Tengo entre 15.000 y 20.000 pantalones de jean azules.
           No sé la cantidad exacta. No sé los precios.
           Paulita tiene un Excel por ahí."
```

### Proceso de Capa 01

```text
intent_type: QUIERE_ENTENDER
dolor expresado: "no sé cuánto tengo, no sé los precios"
clinical_phase_hint: INESTABILIDAD (candidato conversacional)
symptoms_hint: [stock_desordenado, precios_desactualizados] (candidatos)
pathologies_hint: [inventario_no_confiable] (candidato)

CERTEZA:
  - hay stock de pantalones (declarado)
  - hay una persona llamada Paulita
  - hay un Excel (mencionado)

DUDA:
  - Excel_stock_paulita (responsable: Paulita, formato: xlsx)
  - precios_actuales (responsable: Paulita/dueño)

DESCONOCIMIENTO:
  - stock_total_real
  - valor_total_inventario

Tareas:
  TASK_001: pedir Excel a Paulita
  TASK_002: confirmar columnas del Excel
```

### Salida

```text
InitialCaseAdmission:
  intent_type: QUIERE_ENTENDER
  clinical_phase_hint: INESTABILIDAD
  symptoms_hint: [stock_desordenado, precios_desactualizados]
  next_step: "¿Podés pedirle a Paulita el Excel esta semana?"

OwnerDemandCandidate:
  explicit_objective: "Entender cuánto stock tengo y si los precios están bien"
  area_hint: stock
  clarification_needed: false
```

---

## 14. Ejemplo — Perales: caja y sangría

### Entrada

```text
raw_text: "No sé en qué se me va la plata. Tengo caja blanca y caja negra.
           No me dan los números."
```

### Proceso de Capa 01

```text
intent_type: QUIERE_ENTENDER
dolor expresado: "no sé dónde va la plata, no me dan los números"
clinical_phase_hint: SANGRIA (candidato conversacional)
symptoms_hint: [caja_fragmentada, resultado_real_desconocido] (candidatos)

CERTEZA:
  - existe caja blanca
  - existe caja negra

DUDA:
  - reporte_contador_gastos
  - excel_sueldos

DESCONOCIMIENTO:
  - gastos_totales_reales
  - resultado_real
```

### Salida

```text
InitialCaseAdmission:
  intent_type: QUIERE_ENTENDER
  clinical_phase_hint: SANGRIA
  next_step: "Para entender dónde va la plata necesito ventas y gastos del período.
              ¿Podés pedirle al contador el reporte de gastos?"

OwnerDemandCandidate:
  explicit_objective: "Entender dónde se va la plata"
  area_hint: caja
  urgency: 5
```

---

## 15. Reglas rectoras

1. Capa 01 interpreta intención inicial.
2. Capa 01 no diagnostica.
3. Capa 01 no propone acción.
4. Capa 01 no arma caso operativo.
5. Capa 01 recibe `RawInboundEvent` de Capa 00, no entrada cruda directamente.
6. Capa 01 distingue cinco tipos de intención: QUIERE_ENTENDER, QUIERE_ACTUAR, QUIERE_SUBIR_EVIDENCIA, QUIERE_AUTORIZAR, QUIERE_CONSULTAR_ESTADO.
7. El sistema clasifica información en CERTEZA, DUDA o DESCONOCIMIENTO.
8. Toda DUDA genera tarea con responsable, formato esperado y tiempo.
9. El DESCONOCIMIENTO se excluye salvo ROI suficiente.
10. Las fases clínicas, patologías y síntomas son candidatos conversacionales, no hechos confirmados.
11. La semántica PyME (fases, patologías, síntomas) vive en catálogos, Domain Packs o Knowledge Tanks. Capa 01 no la hardcodea.
12. Capa 01 produce `InitialCaseAdmission` y `OwnerDemandCandidate`.
13. Capa 01 deriva evidencia cruda (archivos, imágenes, audios) a Capa 1.5.
14. La mayéutica de Capa 01 es mínima: una pregunta precisa, no un interrogatorio.
15. El dueño es la primera fuente de conocimiento y validación.
16. `OperationalCase` nace mucho después, en Capa 03.

---

## 16. Objetos de Capa 01

### Outputs formales

```text
InitialCaseAdmission
OwnerDemandCandidate
```

### Objetos internos de clasificación

```text
EpistemicState        CERTEZA | DUDA | DESCONOCIMIENTO
IntentType            QUIERE_ENTENDER | QUIERE_ACTUAR | QUIERE_SUBIR_EVIDENCIA |
                      QUIERE_AUTORIZAR | QUIERE_CONSULTAR_ESTADO
Person                persona identificada en la conversación
Source                fuente de información identificada
EvidenceItem          evidencia con estado epistemológico
EvidenceTask          tarea de evidencia pendiente
```

---

## 17. Contratos ya implementados

```text
TS_ADM_001_CONTRATOS_ADMISION
app/contracts/admission_contract.py
tests/contracts/test_admission_contract.py

TS_ADM_002_ADMISSION_SERVICE_MINIMO
app/services/admission_service.py
tests/services/test_admission_service.py
```

**Nota:** Los contratos existentes usan `ClinicalPhase` como Literal hardcodeado.  
En la evolución del sistema, `ClinicalPhase` debe migrar a catálogo externo.  
Los contratos actuales son válidos para V1 mínimo.

---

## 18. Próximos pasos

```text
TS_ADM_003_OWNER_DEMAND_CANDIDATE
  app/contracts/admission_contract.py  (agregar OwnerDemandCandidate)
  → distinguir intent_type
  → agregar clinical_phase_hint como Optional[str] (no Literal)
  → agregar symptoms_hint y pathologies_hint como list[str]

TS_000_001_CONTRATO_RAW_INBOUND_EVENT
  app/contracts/inbound_contract.py
  → RawInboundEvent con todos los campos de Capa 00
```
