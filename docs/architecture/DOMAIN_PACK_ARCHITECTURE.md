# SmartPyme — Arquitectura de Paquetes de Dominio Desmontables

## Estado

Documento conceptual crítico.

Este documento consolida una intuición arquitectónica surgida en conversación:

```text
Los catálogos de SmartPyme son desmontables.
```

Eso significa que SmartPyme no debe entenderse solamente como un software para PyMEs, sino como una instancia particular de un sistema operativo organizacional más general.

---

## Idea central

SmartPyme tiene dos grandes capas:

```text
Motor operativo común
+
Paquete de dominio
```

El motor operativo común puede permanecer estable.

El paquete de dominio puede cambiar.

---

## Fórmula rectora

```text
El sistema operativo es estable.
El dominio es desmontable.
```

---

## Qué significa “dominio desmontable”

Un dominio desmontable es un conjunto de catálogos, narrativas, síntomas, patologías, fórmulas, protocolos, evidencias y skills que especializan el sistema para un tipo de organización.

Ejemplos:

```text
SmartPyme
→ dominio PyME latinoamericana

SmartClinic
→ dominio clínica / salud

SmartSchool
→ dominio escuela / institución educativa

SmartONG
→ dominio organización social

SmartFactory
→ dominio producción industrial
```

El motor no cambia en su lógica central. Cambia el vocabulario, el atlas, las evidencias, las fórmulas y los modelos de interpretación.

---

## Motor operativo común

El motor común conserva la misma estructura para cualquier organización:

```text
recepción
→ conversación mayéutica
→ interpretación
→ curación de datos
→ validación de condiciones
→ formulación de hipótesis
→ construcción de caso operativo
→ investigación
→ reporte diagnóstico
→ propuesta
→ decisión registrada
→ autorización
→ acción controlada
→ trazabilidad
```

Esta estructura no depende específicamente de PyMEs.

Es una arquitectura general para convertir:

```text
dolor organizacional
→ hipótesis
→ evidencia
→ diagnóstico
→ propuesta
→ decisión
→ acción
```

---

## Qué cambia cuando cambia el dominio

Lo que cambia no es el motor. Cambian los catálogos.

Un paquete de dominio puede incluir:

```text
- atlas de síntomas;
- catálogo de patologías;
- catálogo de fórmulas o protocolos;
- catálogo de variables;
- catálogo de evidencia requerida;
- catálogo de skills;
- preguntas mayéuticas;
- lenguaje de reportes;
- modelos organizacionales;
- buenas prácticas;
- criterios de diagnóstico;
- criterios de riesgo;
- criterios de impacto;
- taxonomía propia del dominio.
```

---

## SmartPyme como instancia

SmartPyme es una instancia del sistema general, especializada en PyMEs latinoamericanas.

Su paquete de dominio incluye:

```text
- síntomas PyME;
- patologías PyME;
- modelos operativos PyME;
- fórmulas de margen, stock, caja, costos, producción;
- evidencias como Excel, facturas, POS, extractos, inventarios;
- narrativa del dueño;
- lógica de negocio familiar, artesanal, caótica o personalista;
- problemas de informalidad, desorden, baja digitalización y supervivencia operativa.
```

SmartPyme no debería hardcodear estos conceptos en el core.

Deben vivir en catálogos.

---

## Ejemplo: PyME vs clínica

| Capa | Dominio PyME | Dominio Clínica |
|---|---|---|
| Actor principal | Dueño | Director médico / administrador |
| Dolor | “Estoy perdiendo plata” | “Tenemos demoras o mala atención” |
| Síntoma | Pérdida de margen | Saturación de turnos / baja adherencia |
| Patología | Desalineación costo-precio | Cuello de botella asistencial |
| Evidencia | Excel ventas, facturas, POS | Historia clínica, turnos, estudios |
| Fórmula/protocolo | Margen, stock, conciliación | Indicadores clínicos, protocolos |
| Caso operativo | Investigación de margen | Investigación de flujo asistencial |
| Reporte | Diagnóstico económico-operativo | Diagnóstico clínico-operativo |
| Propuesta | Ajuste precios/proveedores | Rediseño de agenda/protocolo |
| Decisión | Dueño confirma acción | Director autoriza cambio |

El flujo estructural es el mismo.  
La narrativa y la base de conocimiento cambian.

---

## Ejemplo: PyME vs escuela

| Capa | Dominio PyME | Dominio Escuela |
|---|---|---|
| Dolor | “No me cierra la caja” | “Bajó el rendimiento” |
| Síntoma | Descuadre financiero | Deterioro académico |
| Patología posible | Conciliación fallida | Falta de seguimiento pedagógico |
| Evidencia | Extractos, POS, caja diaria | Notas, asistencia, informes docentes |
| Reporte | Hallazgo financiero | Informe pedagógico |
| Acción | Conciliar / corregir procesos | Intervención docente / tutoría |

Nuevamente: el motor no cambia.  
Cambia el paquete semántico.

---

## Separación arquitectónica obligatoria

El core no debe depender de PyME.

```text
Core estable:
- contratos generales;
- recepción;
- curación;
- condiciones;
- decisión;
- autorización;
- caso;
- reporte;
- trazabilidad.

Dominio intercambiable:
- síntomas;
- patologías;
- fórmulas;
- evidencia;
- skills;
- narrativa;
- preguntas;
- buenas prácticas.
```

---

## Regla de diseño

```text
Nunca hardcodear semántica PyME en el core.
La semántica PyME debe vivir en un paquete de dominio.
```

Ejemplo de mala práctica:

```text
core.margin_leak()
core.stock_loss()
core.provider_invoice_required()
```

Ejemplo correcto:

```text
domain_pack_pyme.skills.skill_margin_leak_audit
domain_pack_pyme.evidence.supplier_invoices
domain_pack_pyme.symptoms.sospecha_perdida_margen
```

---

## Nombre de la capa

Nombre técnico sugerido:

```text
Domain Pack
```

Nombre en castellano:

```text
Paquete de dominio
```

Nombre conceptual:

```text
Atlas operativo desmontable
```

---

## Estructura de un Domain Pack

Un paquete de dominio debería incluir, como mínimo:

```text
domain_id
domain_name
domain_description
actors
symptom_catalog
pathology_catalog
operational_models
formula_catalog
protocol_catalog
evidence_catalog
skill_catalog
conditions_catalog
mayeutic_questions
report_language
decision_types
impact_metrics
risk_levels
good_practices
```

---

## Ejemplo conceptual: domain_pack_pyme

```yaml
domain_id: pyme_latam

domain_name: PyME latinoamericana

actors:
  - dueño
  - encargado
  - contador
  - empleado
  - proveedor
  - cliente

symptom_catalog:
  - sospecha_perdida_margen
  - sospecha_faltante_stock
  - descuadre_caja_banco
  - exceso_trabajo_manual
  - incertidumbre_costo_produccion

pathology_catalog:
  - desalineacion_costo_precio
  - costo_reposicion_desactualizado
  - conciliacion_bancaria_fallida
  - falta_automatizacion
  - BOM_incompleto

evidence_catalog:
  - excel_ventas
  - facturas_proveedor
  - extracto_bancario
  - inventario_fisico
  - lista_costos
  - reporte_pos

skill_catalog:
  - skill_margin_leak_audit
  - skill_stock_loss_detect
  - skill_reconcile_bank_vs_pos
  - skill_process_automation_audit
  - skill_bom_cost_audit
```

---

## Ejemplo conceptual: domain_pack_clinica

```yaml
domain_id: clinica_salud

domain_name: Clínica / centro de salud

actors:
  - director_medico
  - administrador
  - medico
  - paciente
  - recepcion
  - obra_social

symptom_catalog:
  - demora_turnos
  - baja_adherencia_tratamiento
  - saturacion_guardia
  - perdida_facturacion_prestaciones
  - desorden_historia_clinica

pathology_catalog:
  - cuello_botella_asistencial
  - agenda_mal_distribuida
  - prestaciones_no_facturadas
  - falta_seguimiento_paciente
  - documentacion_clinica_incompleta

evidence_catalog:
  - agenda_turnos
  - historias_clinicas
  - autorizaciones_obra_social
  - facturacion_prestaciones
  - registros_guardia

skill_catalog:
  - skill_patient_flow_audit
  - skill_medical_billing_reconciliation
  - skill_appointment_bottleneck_detect
  - skill_clinical_record_completeness_audit
```

---

## Método común, narrativa distinta

La metodología sigue siendo la misma:

```text
mayéutica externa
+
hipotético-deductivo interno
```

Pero las preguntas cambian.

### En PyME

```text
¿Tenés ventas y facturas del período?
¿Qué familia de productos querés revisar?
¿Tenés lista de costos?
```

### En clínica

```text
¿Querés revisar turnos, facturación o demora asistencial?
¿Tenés agenda del período?
¿Tenés registros de atención o autorizaciones?
```

La lógica estructural es idéntica.

---

## Relación con la mayéutica

Cada dominio tiene su propia mayéutica.

La mayéutica no es genérica.  
Debe hablar el lenguaje del actor del dominio.

En PyME:

```text
“Para investigar margen necesito ventas y costos.”
```

En clínica:

```text
“Para investigar demora asistencial necesito agenda de turnos, horarios reales de atención y volumen de pacientes.”
```

El método conversacional se mantiene.  
El contenido cambia.

---

## Relación con el método hipotético-deductivo

Cada dominio también tiene sus propias hipótesis.

En PyME:

```text
Investigar si existe pérdida de margen por desalineación costo-precio.
```

En clínica:

```text
Investigar si existe cuello de botella asistencial por distribución ineficiente de turnos.
```

El método es el mismo:

```text
hipótesis
→ evidencia requerida
→ prueba
→ diagnóstico
```

Lo que cambia es la base de conocimiento.

---

## Relación con OperationalCase

El `OperationalCase` debería ser genérico.

No debería ser:

```text
PymeOperationalCase
```

Debería ser:

```text
OperationalCase
```

Y contener un campo como:

```text
domain_id
```
o usar indirectamente `skill_id` y catálogos para resolver dominio.

Ejemplo:

```json
{
  "case_id": "uuid",
  "domain_id": "pyme_latam",
  "cliente_id": "CLIENT_A",
  "job_id": "JOB_123",
  "skill_id": "skill_margin_leak_audit",
  "hypothesis": "Investigar si existe pérdida de margen..."
}
```

---

## Relación con DiagnosticReport

El `DiagnosticReport` también debería ser genérico.

Lo que cambia por dominio es:

```text
- tipo de hallazgo;
- evidencia usada;
- fórmula/protocolo;
- impacto;
- lenguaje del reporte;
- recomendaciones.
```

En PyME, el impacto puede ser:

```text
amount
currency
percentage
units
time_saved
risk_level
```

En clínica, podría incluir además:

```text
tiempo_espera
riesgo_clinico
pacientes_afectados
prestaciones_no_facturadas
```

La estructura general se mantiene.

---

## Relación con ValidatedCaseRecord

El `ValidatedCaseRecord` es el cierre auditable del caso.

Debe ser válido para cualquier dominio.

En PyME, prueba:

```text
se investigó una hipótesis operativa/económica
```

En clínica, prueba:

```text
se investigó una hipótesis clínico-operativa
```

El principio sigue igual:

```text
si no queda registrado, no es auditable;
si no es auditable, no sirve como prueba de valor.
```

---

## Relación con DecisionRecord

El `DecisionRecord` también es genérico.

Todo dominio requiere decisiones trazables.

Ejemplos:

```text
INFORMAR
EJECUTAR
RECHAZAR
```

En otros dominios pueden agregarse decisiones específicas, pero el núcleo se conserva:

```text
qué propuso el sistema
qué respondió el actor autorizado
cuándo lo respondió
qué consecuencia tuvo
```

---

## Arquitectura esperada

```text
Organizational Operating System
│
├── Core
│   ├── recepción
│   ├── conversación
│   ├── curación
│   ├── condiciones
│   ├── casos
│   ├── reportes
│   ├── decisiones
│   ├── autorización
│   └── trazabilidad
│
└── Domain Packs
    ├── domain_pack_pyme
    ├── domain_pack_clinica
    ├── domain_pack_escuela
    ├── domain_pack_ong
    └── domain_pack_factory
```

---

## Implicancia estratégica

SmartPyme puede ser el primer producto, pero no necesariamente el límite del sistema.

El producto base podría llamarse conceptualmente:

```text
Organizational Operating System
```

SmartPyme sería:

```text
Organizational Operating System + Domain Pack PyME
```

Esto permite:

```text
- replicar el sistema en otros sectores;
- vender verticales por dominio;
- reutilizar core;
- crear paquetes semánticos;
- extender habilidades sin reescribir arquitectura;
- separar producto base de especialización sectorial.
```

---

## Riesgo principal

El riesgo es contaminar el core con semántica PyME.

Si eso ocurre, el sistema deja de ser desmontable.

Ejemplos de contaminación:

```text
- que el core asuma siempre “dueño”;
- que el core asuma siempre “margen”;
- que el core asuma siempre “facturas de proveedor”;
- que el core asuma siempre “stock”;
- que el OperationalCase dependa de campos PyME rígidos.
```

Mitigación:

```text
domain_id
catálogos externos
skills por dominio
evidencia por dominio
report language por dominio
```

---

## Principio de portabilidad

```text
Todo concepto de dominio debe poder salir del core y vivir en un catálogo.
```

Si algo no puede moverse a un catálogo, hay que preguntarse si realmente pertenece al core.

---

## Qué debería quedar en el core

```text
- identidad de cliente / organización;
- recepción de demanda;
- interpretación;
- curación;
- validación de condiciones;
- hipótesis;
- caso operativo;
- reporte;
- decisión;
- autorización;
- ejecución controlada;
- trazabilidad;
- auditoría;
- persistencia.
```

---

## Qué debería quedar en Domain Pack

```text
- síntomas;
- patologías;
- fórmulas;
- protocolos;
- skills;
- variables;
- evidencia;
- benchmarks;
- buenas prácticas;
- preguntas mayéuticas;
- lenguaje de reporte;
- tipos de impacto;
- modelos organizacionales.
```

---

## Reglas de implementación futura

1. No hardcodear semántica PyME en core.
2. Crear catálogos por dominio.
3. Mantener contracts genéricos.
4. Agregar `domain_id` cuando sea necesario.
5. Permitir que cada skill declare a qué dominio pertenece.
6. Permitir que cada evidencia tenga tipo y dominio.
7. Permitir que la mayéutica sea configurable por dominio.
8. Permitir que los reportes usen lenguaje del dominio.
9. Mantener DecisionRecord como estructura transversal.
10. Mantener OperationalCase como expediente genérico.

---

## Próximo documento técnico sugerido

```text
DOMAIN_PACK_ARCHITECTURE.md
```

Ruta sugerida:

```text
docs/architecture/DOMAIN_PACK_ARCHITECTURE.md
```

---

## Próximo frente técnico sugerido

```text
TS_027_DOMAIN_PACK_ARCHITECTURE
```

Primero documentación.  
Después implementación mínima.

Implementación mínima futura:

```text
app/catalogs/domain_pack_registry.py
tests/catalogs/test_domain_pack_registry.py
```

Con V1:

```text
domain_pack_pyme
```

Y posibilidad futura de:

```text
domain_pack_clinica
domain_pack_escuela
domain_pack_ong
```

---

## Cierre conceptual

La intuición es correcta y estratégica:

```text
Si cambiamos los catálogos, cambia el dominio.
Si el core se mantiene, el sistema puede operar sobre distintos tipos de organización.
```

SmartPyme es entonces una instancia concreta de una arquitectura mayor.

La clave es no perder esta separación:

```text
Core estable
+
Dominio desmontable
```

Ese principio puede definir el futuro completo del producto.