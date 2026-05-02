# SmartPyme — Diseño conceptual del Catálogo Clínico-Operativo PyME

## Estado

Documento conceptual de continuidad.

Este documento consolida el diseño trabajado en conversación para el próximo frente de SmartPyme:

```text
TS_026C_SYMPTOM_PATHOLOGY_CATALOG
```

No es implementación.  
Es base semántica para convertir el atlas clínico-operativo en catálogo técnico consultable.

---

## Punto de partida

SmartPyme ya tiene documentados y sincronizados los siguientes artefactos:

```text
CONVERSATIONAL_METHODS.md
HYPOTHETICO_DEDUCTIVE_METHOD.md
PYME_SYMPTOM_PATHOLOGY_ATLAS.md
PYME_OPERATIONAL_MODELS_SYMPTOMS_AND_CASES.md
```

Y técnicamente ya puede avanzar hasta:

```text
Pedido del dueño
→ interpretación
→ curación
→ condiciones
→ propuesta
→ decisión registrada
→ autorización
→ Job RUNNING
→ OperationalCase
```

La frontera actual es:

```text
OperationalCase existe.
Todavía no hay investigación técnica ni DiagnosticReport.
```

Antes de generar diagnósticos, necesitamos una pieza intermedia:

```text
Catálogo técnico de síntomas, patologías, hipótesis, skills y evidencia requerida.
```

---

## Nombre conceptual

El componente puede llamarse:

```text
SymptomPathologyCatalog
```

En castellano operativo:

```text
Catálogo clínico-operativo PyME
```

---

## Función del catálogo

La función del catálogo es traducir:

```text
dolor del dueño
→ síntoma operativo
→ patologías posibles
→ hipótesis investigable
→ skill candidata
→ variables necesarias
→ evidencia requerida
→ preguntas mayéuticas
```

Este catálogo no diagnostica.

No dice:

```text
“Hay pérdida de margen.”
```

Dice:

```text
“Si sospechamos pérdida de margen, estas son las patologías posibles,
esta es la hipótesis investigable y estos son los datos necesarios para verificarla.”
```

---

## Regla central

```text
El sistema no pide datos porque sí.
Pide datos porque una hipótesis necesita variables y evidencia para ser verificada.
```

---

## Relación con el método mayéutico

El catálogo ayuda a que la conversación con el dueño sea precisa.

Cuando el dueño expresa un dolor confuso, SmartPyme no debe responder con una batería invasiva de preguntas. Debe hacer pocas preguntas, pero duras y necesarias.

```text
No invasivo en tono.
Duro en condiciones.
```

La mayéutica opera así:

```text
dolor confuso
→ pregunta precisa
→ recorte del problema
→ evidencia necesaria
→ autorización o espera
```

Ejemplo:

```text
“Para investigar pérdida de margen necesito ventas del período,
costos o facturas de proveedor y productos o familias a revisar.
Cuando lo tengas, me lo mandás y seguimos.”
```

---

## Relación con el método hipotético-deductivo

El catálogo también alimenta el razonamiento interno del sistema.

La conversación externa es mayéutica.  
La conversación interna es hipotético-deductiva.

```text
Mayéutica → ayuda al dueño a formular.
Hipotético-deductivo → ayuda al sistema a verificar.
```

El catálogo permite pasar de:

```text
“creo que pierdo plata”
```

a:

```text
Hipótesis:
“Investigar si existe pérdida de margen por desalineación entre costos reales y precios de venta durante un período determinado.”
```

Y desde esa hipótesis deducir:

```text
- ventas reales;
- costos reales o facturas;
- período;
- productos o familias;
- descuentos/promociones si aplican.
```

---

## Estructura conceptual de una entrada del catálogo

Cada entrada del catálogo debería contener:

```text
symptom_id
nombre
dolores_asociados
sintoma_operativo
patologias_posibles
hipotesis_template
skills_candidatas
variables_necesarias
evidenica_requerida
preguntas_mayeuticas
criterios_para_avanzar
criterios_de_bloqueo
notas_semanticas
```

---

## Definiciones

### Dolor del dueño

Formulación humana, inicial y muchas veces imprecisa.

Ejemplos:

```text
“Estoy perdiendo plata.”
“No me cierra la caja.”
“No sé si me falta stock.”
“Trabajo demasiado manual.”
“No sé si producir esto me conviene.”
```

El dolor no es diagnóstico.

---

### Síntoma operativo

Traducción del dolor a una señal observable o investigable.

Ejemplos:

```text
sospecha_perdida_margen
sospecha_faltante_stock
descuadre_caja_banco
exceso_trabajo_manual
incertidumbre_costo_produccion
```

El síntoma no es patología confirmada.

---

### Patología PyME

Patrón recurrente de daño, fricción o desorden operativo.

Ejemplos:

```text
desalineacion_costo_precio
costo_reposicion_desactualizado
descuentos_no_controlados
merma_stock
ventas_no_registradas
conciliacion_bancaria_fallida
falta_automatizacion
BOM_incompleto
```

La patología posible no es hallazgo.

---

### Hipótesis investigable

Formulación verificable, no afirmativa.

Ejemplo correcto:

```text
Investigar si existe pérdida de margen por desalineación entre costos reales y precios de venta durante {periodo}.
```

Ejemplo incorrecto:

```text
Hay pérdida de margen.
```

---

### Skill candidata

Capacidad técnica que puede investigar esa hipótesis.

Ejemplos:

```text
skill_margin_leak_audit
skill_stock_loss_detect
skill_reconcile_bank_vs_pos
skill_process_automation_audit
skill_bom_cost_audit
```

La skill no decide.  
La skill ejecuta una investigación bajo condiciones.

---

### Variables necesarias

Datos escalares mínimos para verificar la hipótesis.

Ejemplos:

```text
periodo
productos_o_familias
margen_esperado
precio_venta_real
costo_reposicion
stock_teorico
stock_fisico
bank_total
pos_total
```

---

### Evidencia requerida

Fuentes o documentos necesarios para contrastar.

Ejemplos:

```text
ventas_pos
excel_ventas
facturas_proveedor
extracto_bancario
inventario_fisico
lista_costos
reporte_promociones
descripcion_flujo_manual
```

---

## Entrada ejemplo 1: sospecha de pérdida de margen

```yaml
symptom_id: sospecha_perdida_margen

nombre: Sospecha de pérdida de margen

dolores_asociados:
  - "pierdo plata"
  - "vendo pero no gano"
  - "no me deja margen"
  - "los proveedores aumentaron"
  - "no sé si estoy vendiendo bien"
  - "me aumentaron los costos"
  - "no sé si los precios están actualizados"

sintoma_operativo:
  Sospecha de deterioro del margen real frente al margen esperado.

patologias_posibles:
  - desalineacion_costo_precio
  - costo_reposicion_desactualizado
  - descuentos_no_controlados
  - mix_productos_deteriorado
  - comisiones_impuestos_no_imputados
  - merma_stock_impactando_margen

hipotesis_template:
  "Investigar si existe pérdida de margen por desalineación entre costos reales y precios de venta durante {periodo}."

skills_candidatas:
  - skill_margin_leak_audit

variables_necesarias:
  - periodo
  - productos_o_familias
  - margen_esperado
  - precio_venta_real
  - costo_reposicion

evidenica_requerida:
  - ventas_pos
  - excel_ventas
  - facturas_proveedor
  - lista_costos
  - promociones_descuentos
  - inventario_merma_si_aplica

preguntas_mayeuticas:
  - "¿Qué período querés revisar?"
  - "¿Querés revisar todos los productos o una familia puntual?"
  - "¿Tenés ventas y facturas de proveedor de ese período?"
  - "¿Tenés una lista de precios o costos actualizada?"

criterios_para_avanzar:
  - existe demanda_original
  - existe periodo o posibilidad de pedirlo
  - existe evidencia de ventas o costos
  - existe skill candidata

criterios_de_bloqueo:
  - no hay ventas ni costos
  - no hay período
  - no hay productos o familias identificables
```

---

## Entrada ejemplo 2: sospecha de faltante de stock

```yaml
symptom_id: sospecha_faltante_stock

nombre: Sospecha de faltante o pérdida de stock

dolores_asociados:
  - "no sé si me falta stock"
  - "el inventario no coincide"
  - "compro pero no aparece"
  - "me desaparecen productos"
  - "no me cierran las cantidades"
  - "tengo diferencias entre sistema y depósito"

sintoma_operativo:
  Diferencia sospechada entre stock teórico y stock físico.

patologias_posibles:
  - merma
  - robo_hormiga
  - ventas_no_registradas
  - compras_no_asentadas
  - errores_de_carga
  - ajustes_de_stock_no_documentados

hipotesis_template:
  "Investigar si existe faltante de stock comparando stock teórico, ventas, compras e inventario físico durante {periodo}."

skills_candidatas:
  - skill_stock_loss_detect

variables_necesarias:
  - periodo
  - productos_o_familias
  - stock_teorico
  - stock_fisico
  - ajuste_merma

evidenica_requerida:
  - inventario_fisico
  - ventas_pos
  - compras
  - ajustes_stock
  - movimientos_deposito

preguntas_mayeuticas:
  - "¿Querés revisar todos los productos o una familia puntual?"
  - "¿Tenés inventario físico reciente?"
  - "¿Tenés ventas y compras del período?"
  - "¿Hay ajustes manuales de stock?"

criterios_para_avanzar:
  - existe stock físico o stock teórico
  - existe período
  - existe evidencia de ventas/compras o inventario

criterios_de_bloqueo:
  - no hay inventario ni ventas/compras
  - no hay producto/familia a revisar
```

---

## Entrada ejemplo 3: descuadre caja/banco

```yaml
symptom_id: descuadre_caja_banco

nombre: Diferencia entre caja, ventas y banco

dolores_asociados:
  - "no me cierra la caja"
  - "no me cierra el banco"
  - "me falta plata"
  - "las ventas no coinciden con los depósitos"
  - "no sé dónde está la diferencia"
  - "Mercado Pago no me coincide"

sintoma_operativo:
  Diferencia entre ventas registradas, cobros y depósitos bancarios.

patologias_posibles:
  - conciliacion_bancaria_fallida
  - ventas_no_registradas
  - comisiones_no_consideradas
  - retiros_no_documentados
  - diferencias_por_medios_de_pago
  - errores_de_cierre_de_caja

hipotesis_template:
  "Investigar si existe descuadre entre ventas registradas, cobros y depósitos bancarios durante {periodo}."

skills_candidatas:
  - skill_reconcile_bank_vs_pos

variables_necesarias:
  - periodo
  - pos_total
  - bank_total
  - medios_de_pago

evidenica_requerida:
  - extracto_bancario
  - reporte_pos
  - caja_diaria
  - liquidaciones_mp_tarjetas
  - comprobantes_retiros

preguntas_mayeuticas:
  - "¿Qué período querés conciliar?"
  - "¿Tenés extracto bancario y reporte de ventas?"
  - "¿Querés comparar banco contra POS, caja diaria o Mercado Pago?"
  - "¿Hay retiros o gastos en efectivo no registrados?"

criterios_para_avanzar:
  - existe período
  - existe al menos una fuente de ventas
  - existe al menos una fuente bancaria/cobro

criterios_de_bloqueo:
  - no hay extracto ni reporte de ventas
  - no hay período
```

---

## Entrada ejemplo 4: exceso de trabajo manual

```yaml
symptom_id: exceso_trabajo_manual

nombre: Repetición operativa innecesaria

dolores_asociados:
  - "trabajo demasiado manual"
  - "pasamos muchos Excel a mano"
  - "dependo de una persona para cargar todo"
  - "se repite el mismo trabajo todas las semanas"
  - "perdemos tiempo copiando datos"
  - "hay errores por carga manual"

sintoma_operativo:
  Flujo operativo repetitivo, manual y propenso a errores.

patologias_posibles:
  - falta_automatizacion
  - duplicacion_de_carga
  - dependencia_de_personas
  - ausencia_de_integracion
  - riesgo_error_humano
  - perdida_tiempo_operativo

hipotesis_template:
  "Investigar si existe pérdida de tiempo y riesgo operativo por repetición manual de tareas en el flujo {flujo_operativo}."

skills_candidatas:
  - skill_process_automation_audit

variables_necesarias:
  - frecuencia
  - tiempo_dedicado
  - personas_involucradas
  - archivos_usados
  - flujo_operativo

evidenica_requerida:
  - descripcion_flujo
  - archivos_excel
  - capturas_pantalla
  - pasos_del_proceso
  - frecuencia_tarea
  - responsables

preguntas_mayeuticas:
  - "¿Qué tarea se repite?"
  - "¿Cada cuánto se hace?"
  - "¿Cuántas personas intervienen?"
  - "¿Qué archivos o sistemas usan?"
  - "¿Dónde suelen aparecer errores?"

criterios_para_avanzar:
  - existe descripción del flujo
  - existe frecuencia o tiempo estimado
  - existe evidencia mínima del proceso

criterios_de_bloqueo:
  - no se describe el flujo
  - no se identifica tarea concreta
```

---

## Entrada ejemplo 5: incertidumbre de costo de producción

```yaml
symptom_id: incertidumbre_costo_produccion

nombre: Incertidumbre sobre costo real de producción

dolores_asociados:
  - "no sé si gano plata produciendo esto"
  - "no sé cuánto me cuesta fabricar"
  - "no tengo claro el costo de materia prima"
  - "no sé si el precio final está bien"
  - "no sé si conviene producirlo"
  - "no tengo armado el cálculo de producción"

sintoma_operativo:
  Falta de claridad sobre costo unitario real, margen productivo o precio final.

patologias_posibles:
  - BOM_incompleto
  - costos_indirectos_no_imputados
  - materia_prima_sin_costo_actualizado
  - mano_obra_no_considerada
  - merma_productiva_no_contemplada
  - precio_final_desalineado

hipotesis_template:
  "Investigar si el producto {producto} tiene costo de producción completo y margen suficiente considerando materia prima, mano de obra, merma y costos indirectos."

skills_candidatas:
  - skill_bom_cost_audit

variables_necesarias:
  - producto
  - lista_materiales
  - cantidades_por_producto
  - costo_unitario_materiales
  - mano_obra
  - merma
  - precio_final

evidenica_requerida:
  - receta_o_BOM
  - facturas_materia_prima
  - lista_costos
  - hoja_produccion
  - precio_venta
  - tiempos_produccion

preguntas_mayeuticas:
  - "¿Qué producto querés revisar?"
  - "¿Tenés lista de materiales o receta?"
  - "¿Tenés costos unitarios de materia prima?"
  - "¿Querés incluir mano de obra, merma y costos indirectos?"
  - "¿Tenés precio final de venta?"

criterios_para_avanzar:
  - existe producto
  - existe al menos lista de materiales o costos de materia prima
  - existe precio final o margen esperado

criterios_de_bloqueo:
  - no hay producto definido
  - no hay materiales ni costos
```

---

## Relación con catálogos ya existentes

Este catálogo se ubica antes de:

```text
operational_conditions_catalog.py
```

El atlas/catálogo clínico-operativo responde:

```text
¿Por qué esta demanda lleva a esta skill?
```

El catálogo de condiciones responde:

```text
¿Qué datos hacen falta para ejecutar esta skill?
```

La curación de datos responde:

```text
¿Los datos que llegaron son válidos, limpios y relevantes?
```

El OperationalCase responde:

```text
¿Ya tenemos expediente investigable?
```

El DiagnosticReport responderá:

```text
¿Qué se encontró y con qué evidencia?
```

---

## Secuencia completa esperada

```text
Dueño expresa dolor
→ sistema detecta síntoma operativo
→ consulta SymptomPathologyCatalog
→ obtiene patologías posibles
→ formula hipótesis investigable
→ propone skill candidata
→ deduce variables/evidencia requerida
→ pregunta mayéuticamente lo mínimo necesario
→ recibe evidencia
→ cura datos
→ valida condiciones
→ crea OperationalCase
→ investiga
→ genera DiagnosticReport
→ consolida ValidatedCaseRecord
→ pregunta al dueño el siguiente paso
```

---

## Reglas semánticas

1. El dolor del dueño no es diagnóstico.
2. El síntoma operativo no es patología confirmada.
3. La patología posible no es hallazgo.
4. La hipótesis no afirma: investiga.
5. La skill no decide: ejecuta bajo condiciones.
6. El catálogo no diagnostica: orienta.
7. El sistema no pide datos porque sí.
8. El sistema pide evidencia porque una hipótesis la necesita.
9. Si falta evidencia mínima, se devuelve la pelota al dueño.
10. Si no hay material suficiente, no se crea OperationalCase.
11. Sin evidencia trazable, no hay diagnóstico confirmado.
12. Sin diferencia cuantificada, no hay hallazgo accionable.

---

## Criterios de diseño del catálogo técnico

Cuando se implemente en código, debe cumplir:

```text
- determinístico;
- auditable;
- versionable;
- legible;
- extensible;
- no dependiente de IA;
- no generador de diagnóstico;
- conectado a skills y condiciones.
```

Debe permitir operaciones como:

```text
get_symptom(symptom_id)
match_symptoms_from_owner_message(message)
get_candidate_pathologies(symptom_id)
get_candidate_skills(symptom_id)
get_required_variables(symptom_id)
get_required_evidenice(symptom_id)
get_mayeutic_questions(symptom_id)
```

Pero en V1 conviene evitar sobreingeniería.

Primero:

```text
catálogo estático + tests
```

Después:

```text
macher
```

Después:

```text
integración con intake
```

---

## Riesgos

### 1. Diagnóstico prematuro

Riesgo: que el sistema trate una patología posible como confirmada.

Mitigación:

```text
todo entra como hipótesis investigable
```

---

### 2. Preguntas excesivas

Riesgo: que el sistema abrume al dueño.

Mitigación:

```text
preguntas mínimas necesarias
```

---

### 3. Catálogo demasiado académico

Riesgo: usar categorías corporativas que no sirven para PyMEs latinoamericanas artesanales, familiares y caóticas.

Mitigación:

```text
castellano operativo
dolores reales
evidenica concreta
skills accionables
```

---

### 4. Datos pedidos sin explicación

Riesgo: que el dueño no entienda por qué se le pide algo.

Mitigación:

```text
explicar siempre para qué se pide la evidencia
```

---

### 5. Mezclar atlas con condiciones

Riesgo: confundir “por qué esta skill” con “qué necesita esta skill”.

Mitigación:

```text
Atlas/Catálogo clínico-operativo = por qué
OperationalConditionsCatalog = qué hace falta
```

---

## Próximo frente técnico sugerido

```text
TS_026C_SYMPTOM_PATHOLOGY_CATALOG
```

Objetivo:

```text
Convertir este diseño en catálogo técnico consultable.
```

Alcance mínimo recomendado:

```text
app/catalogs/symptom_pathology_catalog.py
tests/catalogs/test_symptom_pathology_catalog.py
```

Sin integración todavía.

---

## Cierre conceptual

Este catálogo es una pieza clave porque conecta el lenguaje humano del dueño con la arquitectura operativa del sistema.

Sin este catálogo, SmartPyme puede validar condiciones de una skill, pero no puede explicar por qué llegó a esa skill.

Con este catálogo, el sistema puede decir:

```text
Te pido ventas y facturas no porque sí,
sino porque para verificar pérdida de margen necesito comparar precio real contra costo real.
```

Esa explicación convierte al sistema en una herramienta confiable, auditada y pedagógica.