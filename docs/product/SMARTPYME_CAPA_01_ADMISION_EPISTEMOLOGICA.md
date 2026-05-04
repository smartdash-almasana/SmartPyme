# SmartPyme — Capa 01: Admisión Epistemológica

## Estado

PROPUESTA CANONICA — REQUIERE ALINEACION CON CAPA 1.5 Y CAPA 02

---

## Propósito

Este documento define la Capa 1 de SmartPyme.

Su objetivo es consolidar la lógica de la primera interacción entre el dueño y el sistema:

- admisión semántica;
- inteligencia epistemológica;
- anamnesis operativa;
- construcción inicial del caso;
- identificación de evidencia, personas, fuentes y tareas.

Esta capa es el fundamento de toda investigación posterior.

---

## Principio fundamental

SmartPyme no es un chatbot de respuestas rápidas.

SmartPyme es un sistema clínico-operativo que inicia su proceso con una anamnesis del negocio para construir un caso investigable.

La primera interacción no está diseñada para resolver la demanda ni diagnosticar. Está diseñada para leer correctamente el enunciado del dueño, ordenar el problema y preparar el caso inicial.

Frase rectora:

> Toda buena lectura del enunciado anuncia una mejor resolución del problema.

---

## Qué hace la admisión

La capa de admisión:

- escucha el planteo inicial del dueño;
- identifica el dolor o demanda inicial;
- reconstruye contexto mínimo del negocio;
- clasifica la información según estado epistemológico;
- identifica CERTEZA, DUDA y DESCONOCIMIENTO;
- detecta la fase clínica del problema;
- mapea personas, fuentes y evidencias;
- registra responsables, formatos y tiempos;
- relaciona la demanda con patologías candidatas;
- prioriza por ROI;
- genera tareas pendientes de evidencia;
- produce un objeto `InitialCaseAdmission`.

---

## Qué no hace la admisión

La capa de admisión no:

- diagnostica;
- calcula fórmulas finales;
- emite juicios de valor;
- propone tratamientos o soluciones definitivas;
- ejecuta acciones;
- crea un `OperationalCase` completo;
- reemplaza la validación del dueño;
- inventa datos faltantes;
- fuerza una hipótesis libre.

---

## Flujo de Capa 1

```text
Dueño habla
→ sistema recibe demanda
→ identifica dolor inicial
→ realiza anamnesis operativa
→ clasifica CERTEZA / DUDA / DESCONOCIMIENTO
→ identifica personas, fuentes y evidencias
→ detecta fase clínica
→ relaciona con patologías candidatas
→ genera tareas de evidencia
→ prioriza por ROI
→ produce InitialCaseAdmission
→ pide validación del dueño
```

---

## Inteligencia epistemológica

La inteligencia epistemológica es el núcleo de la admisión.

SmartPyme no trata toda la información como equivalente. Cada bloque de información aportado por el dueño debe clasificarse según su estado de conocimiento.

### CERTEZA

Información disponible, afirmada como existente o verificable.

Ejemplo:

```text
"Esta semana vendí 300.000 pesos."
```

Una certeza puede tener distintos niveles de confianza. Una cifra recordada por el dueño puede ser certeza declarada, pero no evidencia documental fuerte.

Acción:

```text
CERTEZA → permite avanzar, pero puede requerir corroboración.
```

---

### DUDA

Información que podría existir, pero no está disponible o confirmada en el momento.

Ejemplo:

```text
"Paulita tiene un Excel por ahí."
```

Acción:

```text
DUDA → genera tarea.
```

Toda DUDA debe registrar:

- responsable;
- fuente probable;
- formato esperado;
- fecha o tiempo estimado;
- acción de seguimiento.

Ejemplo:

```text
EVIDENCIA: Excel_stock
ESTADO: DUDA
RESPONSABLE: Paulita
FORMATO: Excel
ACCION: pedir archivo
```

---

### DESCONOCIMIENTO

Información inexistente, inaccesible o desconocida por completo.

Ejemplo:

```text
"No tengo idea del stock real."
```

Acción:

```text
DESCONOCIMIENTO → queda fuera del alcance inicial, salvo ROI suficiente.
```

El desconocimiento no se inventa. Se deja marcado y solo se construye desde cero si el impacto lo justifica.

---

## Regla epistemológica central

```text
CERTEZA → permite avanzar
DUDA → genera tarea
DESCONOCIMIENTO → se excluye salvo ROI suficiente
```

---

## Grafo de acceso a evidencia

La conversación del dueño revela una red organizacional.

SmartPyme debe registrar:

- personas;
- roles;
- fuentes;
- evidencias;
- responsables;
- formatos;
- tiempos;
- accesibilidad.

### Entidades mínimas

```text
PERSONA:
  nombre
  rol
  contacto opcional

FUENTE:
  tipo
  formato
  responsable
  ubicación

EVIDENCIA:
  tipo
  fuente
  responsable
  estado epistemológico
```

### Relaciones

```text
PERSONA --gestiona--> FUENTE
FUENTE --contiene--> EVIDENCIA
EVIDENCIA --habilita--> FORMULA
FORMULA --produce--> RESULTADO
RESULTADO --requiere--> VALIDACION_DUEÑO
```

La admisión transforma conversación humana en logística de evidencia.

---

## Fases clínicas

La admisión debe clasificar el problema según fase clínica.

### SANGRIA

Hay pérdida económica activa o sospecha fuerte de pérdida.

Ejemplos:

```text
"No sé dónde se me va la plata."
"No me dan los números."
"Creo que me están robando."
"Vendo pero no queda nada."
```

Prioridad máxima.

---

### INESTABILIDAD

Hay desorden operativo que impide controlar el negocio.

Ejemplos:

```text
"No sé cuánto stock tengo."
"No sé los precios."
"Todo depende de Paulita."
"Tengo ventas por WhatsApp sin consolidar."
```

Prioridad alta.

---

### OPTIMIZACION

El negocio funciona, pero busca mejorar.

Ejemplos:

```text
"Quiero vender más."
"Quiero automatizar."
"Quiero mejorar margen."
"Quiero ahorrar tiempo."
```

Prioridad posterior.

---

## Prioridad clínica

```text
SANGRIA > INESTABILIDAD > OPTIMIZACION
```

Regla:

> Primero detener pérdida, después estabilizar, después optimizar.

---

## ROI como gobierno de prioridad

ROI no significa solo retorno financiero.

Incluye:

- ahorro de tiempo;
- ahorro de dinero;
- dinero recuperado;
- riesgo reducido;
- ganancia potencial;
- costo de obtener evidencia;
- costo de ejecutar una acción;
- tiempo a valor.

La admisión no calcula ROI final, pero usa ROI para decidir:

- qué preguntar primero;
- qué evidencia pedir primero;
- qué tarea crear primero;
- qué fase atacar primero;
- qué dejar fuera de alcance.

Regla conceptual:

```text
priorizar lo que:
  reduzca sangría
  tenga impacto económico alto
  requiera poca evidencia
  entregue valor rápido
```

---

## Catálogo vs Knowledge Tank

### Catálogo de patologías

Sirve para:

- clasificar el problema;
- mapear síntomas;
- detectar patologías candidatas;
- activar casos operativos candidatos.

No debe contener lógica matemática profunda.

---

### Knowledge Tank

Sirve para:

- fórmulas;
- métodos;
- protocolos;
- modelos financieros;
- modelos de stock;
- modelos de caja;
- modelos de margen;
- conocimiento externo.

---

## Regla de separación

```text
Catálogo clasifica.
Knowledge Tank calcula o fundamenta.
Caso operativo conecta.
```

---

## Output de admisión

El único y exclusivo output de la Capa 1 es un objeto `InitialCaseAdmission`, que consolida:

- demanda original;
- personas;
- fuentes;
- evidencias;
- tareas;
- fase clínica;
- síntomas candidatos;
- patologías candidatas;
- próximo paso sugerido.

No es un diagnóstico.

---

## Diferencia entre InitialCaseAdmission y OperationalCase

### InitialCaseAdmission

Es el resultado de la primera conversación.

Documenta:

- entendimiento inicial;
- evidencia disponible;
- evidencia faltante;
- personas involucradas;
- fuentes detectadas;
- tareas pendientes;
- fase clínica;
- patologías candidatas.

Su propósito es validar el punto de partida con el dueño.

---

### OperationalCase

Nace después, en una cadena de capas posterior.

InitialCaseAdmission no pasa directamente a OperationalCase.
Primero debe alimentar Capa 1.5 (Normalización Documental) para producir un NormalizedEvidencePackage.
Luego Capa 02 (Activación de Conocimiento e Investigación) produce un OperationalCaseCandidate.
El OperationalCase completo nace después de validación del dueño, evidencia suficiente y decisión arquitectónica posterior.

Solo debe crearse cuando:

- existe evidencia mínima;
- hay condiciones suficientes;
- el dueño validó el punto de partida;
- el sistema puede iniciar una investigación formal.

Es un expediente técnico, no un output de admisión.

---

## Caso humano 1 — Textil Perales: stock y precios

### Demanda inicial

```text
Tengo entre 15.000 y 20.000 pantalones de jean azules.
No sé la cantidad exacta.
No sé los precios.
Los tengo desactualizados.
Paulita tiene un Excel por ahí.
Los vendo a revendedores.
Cuando viene un vendedor, le mando WhatsApp a Paulita para que lo anote.
```

### Lectura de admisión

El sistema detecta:

```text
stock_desordenado
precios_desactualizados
registro_ventas_indirecto
flujo_manual_con_intermediario
control_operativo_fragil
```

### Fase clínica

```text
INESTABILIDAD
```

### Información cierta

```text
rubro: textil
producto: pantalones de jean
stock aproximado declarado: 15.000–20.000
canal de venta: revendedores
persona administrativa: Paulita
registro operativo: WhatsApp → Paulita → Excel
```

### Información dudosa

```text
Excel_stock_paulita:
  estado: DUDA
  responsable: Paulita
  formato: Excel
  acción: pedir archivo

precios_actuales:
  estado: DUDA
  responsable: Paulita / dueño
  formato: Excel o lista informal
  acción: validar precios vigentes
```

### Desconocimiento

```text
stock_total_real:
  estado: DESCONOCIMIENTO
  motivo: no existe conteo actual confirmado

valor_total_inventario:
  estado: DESCONOCIMIENTO
  motivo: requiere stock real + precio/costo
```

### Tareas pendientes

```text
TASK_001:
  responsable: dueño
  objetivo: pedir a Paulita el Excel de stock/precios

TASK_002:
  responsable: dueño / Paulita
  objetivo: confirmar si el Excel contiene modelo, talle, color, cantidad y precio

TASK_003:
  responsable: sistema
  objetivo: evaluar si el Excel sirve como base o si hace falta conteo físico estructurado
```

---

## Caso humano 2 — Textil Perales: caja blanca, caja negra y sangría

### Demanda inicial

```text
Tengo dos cajas.
Una caja en blanco que le mando al contador.
Después tengo pagos en negro a empleados.
Tengo una caja negra que no paga impuestos.
No sé en qué se me va la plata.
No me dan los números.
No sé cuánto gasto.
No sé si puedo ahorrar.
No sé si me están robando.
```

### Fase clínica

```text
SANGRIA
```

Porque el dueño expresa pérdida de control económico.

### Síntomas detectados

```text
caja_fragmentada
gastos_no_consolidados
resultado_real_desconocido
control_financiero_incompleto
imposibilidad_de_calcular_ganancia
riesgo_de_sangria_economica
```

### Evidencia cierta

```text
existe contador
existe caja blanca
existe caja negra
existe Excel de sueldos blanco + negro
```

### Evidencia dudosa

```text
Reporte_contador_gastos:
  estado: DUDA
  responsable: contador
  función: obtener gastos blancos

Excel_sueldos:
  estado: DUDA
  responsable: dueño
  función: consolidar pagos en blanco y negro
```

### Desconocimiento

```text
gastos_totales_reales:
  estado: DESCONOCIMIENTO
  motivo: requiere integrar caja blanca + caja negra

resultado_real:
  estado: DESCONOCIMIENTO
  motivo: requiere ventas reales - gastos reales

sangria_exacta:
  estado: DESCONOCIMIENTO
  motivo: requiere consolidación documental
```

### Tareas pendientes

```text
TASK_001:
  responsable: dueño
  objetivo: pedir al contador reporte de gastos blancos del mes

TASK_002:
  responsable: dueño
  objetivo: subir Excel de sueldos blanco + negro

TASK_003:
  responsable: sistema
  objetivo: consolidar ingresos y egresos reales cuando llegue evidencia
```

---

## Contrato programático futuro

La futura implementación Python debería partir de estos objetos:

```text
EpistemicState
ClinicalPhase
EvidenceAvailability
TaskStatus
Area
Person
Source
EvidenceItem
EvidenceTask
OwnerDemand
SymptomCandidate
PathologyCandidate
InitialCaseAdmission
```

Servicio futuro:

```python
AdmissionService.process(
    cliente_id: str,
    owner_message: str
) -> InitialCaseAdmission
```

La primera implementación debe ser mínima y determinística.

---

## Reglas rectoras

1. SmartPyme no responde como chatbot; construye un caso.
2. La primera interacción no diagnostica.
3. El sistema clasifica información en CERTEZA, DUDA o DESCONOCIMIENTO.
4. Toda DUDA genera tarea con responsable, formato esperado y tiempo.
5. El DESCONOCIMIENTO se excluye salvo ROI suficiente.
6. El dueño es la primera fuente de conocimiento y validación.
7. La admisión detecta fase clínica: SANGRIA, INESTABILIDAD u OPTIMIZACION.
8. La prioridad está gobernada por ROI.
9. El Catálogo clasifica patologías.
10. El Knowledge Tank contiene fórmulas, métodos y protocolos.
11. El output de admisión es `InitialCaseAdmission`.
12. `OperationalCase` nace después.
13. La admisión no define todavía diagnóstico ni ejecución.
14. Cada ciclo posterior debe cerrar con validación del dueño.

---

## Próximo paso

Implementar contratos Pydantic mínimos para representar `InitialCaseAdmission` y sus objetos componentes.

TaskSpec sugerida:

```text
TS_ADM_001_CONTRATOS_ADMISION
```
