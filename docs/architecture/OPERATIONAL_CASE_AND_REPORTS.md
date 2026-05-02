# Operational Case and Diagnostic Reports Contract

## 1. Introducción
Este documento define la columna vertebral documental del flujo investigativo de SmartPyme. Establece los contratos que permiten pasar de una autorización formal del dueño a un diagnóstico auditable y cuantificable.

## 2. Diferenciación de Registros
Para garantizar la trazabilidad y la soberanía del sistema, se distinguen cuatro tipos de registros:

- **DecisionRecord:** Decisión o autorización formal del dueño (INFORMAR, EJECUTAR, RECHAZAR).
- **OperationalCase:** Expediente técnico armado para la investigación (Hipótesis).
- **DiagnosticReport:** Resultado documentado del proceso de investigación (Hallazgos).
- **ValidatedCaseRecord:** Cierre consolidado y auditable de la investigación.

## 3. Flujo Operativo
1. **DecisionRecord (Tipo EJECUTAR):** El dueño autoriza la propuesta.
2. **Job RUNNING:** El motor de orquestación activa el trabajo.
3. **OperationalCase:** Se construye el expediente investigativo con una hipótesis falsable.
4. **DiagnosticReport:** Los motores de análisis generan hallazgos basados en evidencia.
5. **ValidatedCaseRecord:** Se consolida el caso para auditoría y cierre.
6. **Nueva pregunta al dueño:** Se presenta el resultado para la siguiente decisión.

## 4. Definición de Contratos

### 4.1 OperationalCase (Expediente)
Representa el "Qué vamos a buscar". Empieza siempre con una hipótesis investigable, nunca con un diagnóstico pre-concebido.

- **case_id:** UUID
- **cliente_id:** str
- **job_id:** str
- **skill_id:** str
- **demanda_original:** str (Input crudo del dueño)
- **hypothesis:** str (Ejemplo: "¿Existen discrepancias entre facturas de proveedores y remitos de almacén en el periodo X?")
- **taxonomia_pyme:** dict (Contexto de industria/proceso)
- **variables_curadas:** dict (Datos limpios: periodos, montos, IDs)
- **evidencia_disponible:** list[str] (IDs de chunks/documentos)
- **condiciones_validadas:** list[str] (Checks de viabilidad técnica)
- **formula_aplicable:** str (ID del cálculo determinístico)
- **patologia_posible:** str (Anomalía objetivo)
- **investigation_plan:** list[str] (Pasos para el motor técnico)

### 4.2 DiagnosticReport (Resultado)
Representa el "Qué descubrimos". No puede confirmar un hallazgo sin evidencia trazable.

- **report_id:** UUID
- **case_id:** str
- **diagnosis_status:** `CONFIRMED` | `NOT_CONFIRMED` | `INSUFFICIENT_EVIDENCE`
- **findings:** list[Finding]
- **quantified_impact:** Impact
- **reasoning_summary:** str
- **proposed_next_actions:** list[str]
- **owner_question:** str (Pregunta cerrada para el próximo paso)

**Estructura de Finding:**
- **entity:** Objeto analizado (ej. "Factura A-001")
- **finding_type:** Tipo de anomalía (ej. "DUPLICATE", "MISSING_MATCH")
- **measured_difference:** Diferencia detectada (valor vs esperado)
- **compared_sources:** Fuentes contrastadas
- **evidence_used:** list[str] (IDs de evidencia vinculantes)
- **severity:** `LOW` | `MEDIUM` | `HIGH` | `CRITICAL`
- **recommendation:** str

**Estructura de Impact:**
- **amount:** float
- **currency:** str
- **percentage:** float
- **units:** int
- **time_saved:** str (ISO Duration)
- **risk_level:** `LOW` | `MEDIUM` | `HIGH`

### 4.3 ValidatedCaseRecord (Cierre Auditable)
Representa el "Registro Inmutable" de la investigación terminada.

- **validated_case_id:** UUID
- **timestamp:** ISO UTC
- **hypothesis:** str
- **diagnosis_status:** str
- **evidence_used:** list[str]
- **findings_summary:** str
- **quantified_impact:** Impact
- **owner_visible_report:** str (Markdown formateado para el dueño)
- **next_question:** str

## 5. Reglas Semánticas
1. **Hipótesis Primero:** Un caso operativo no puede ser "Revisar stock"; debe ser "Investigar si existe pérdida de margen en el almacén X durante el período Y".
2. **Evidencia Obligatoria:** Ningún `DiagnosticReport` puede confirmar un hallazgo sin `evidence_used` trazable al `EvidenceStore`.
3. **Cuantificación Requerida:** Todo reporte debe intentar expresar el impacto en el objeto `Impact` para justificar el valor de la investigación.
