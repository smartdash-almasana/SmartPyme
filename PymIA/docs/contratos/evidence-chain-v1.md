<!--
FUENTE_ORIGINAL: docs/product/EVIDENCE_CHAIN_CONTRACT_V1.md
ESTADO: normalizado_minimo
NORMALIZACION: removida sección 10 "Conformidad con Fact Factory" — contiene referencia a factory/evidence/ y placeholder [COMMIT_HASH] irrelevantes para PymIA
-->

# Evidence Chain Contract V1

**Estado:** HITO_08_EVIDENCE_CHAIN_CONTRACT_V1  
**Capa:** PRODUCT_CONTRACTS  
**Fecha de establecimiento:** 2026-05-05  
**Objeto:** Establecer los invariantes y estructura de una cadena de evidencia dentro del sistema SmartPyme, para garantizar trazabilidad completa, fuentes verificables y separación clara entre observación, inferencia y decisión.

---

## 1. Campos obligatorios

Cada Evidence Chain V1 debe ser un objeto JSON con los siguientes campos obligatorios:

| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `evidence_chain_id` | string (UUID v4) | Identificador único de la cadena, generado por el sistema en el momento de creación. | `"ec_550e8400-e29b-41d4-a716-446655440000"` |
| `cliente_id` | string (no vacío) | Identificador del cliente (organización, empresa, persona) al que pertenece la evidencia. **Obligatorio**; no puede ser nulo ni vacío. | `"cliente_acme_sa"` |
| `source_payload_id` | string (UUID v4) | Referencia al payload crudo (Capa 0) que originó la cadena. Vincula cada elemento de evidencia a la fuente primaria. | `"pay_550e8400-e29b-41d4-a716-446655440000"` |
| `primary_evidence` | array de objetos | Lista de evidencias primarias extraídas del payload. Cada elemento tiene `type`, `content`, `extracted_at`, `extracted_by`, `confidence`. | Ver sección 2. |
| `extracted_facts` | array de objetos | Hechos estructurados derivados de la evidencia primaria. Cada hecho tiene `fact_id`, `description`, `source_evidence_index`, `validated`. | Ver sección 3. |
| `validations` | array de objetos | Validaciones aplicadas a cada hecho (cross-check, regla de negocio, consistencia). Cada validación tiene `validation_id`, `fact_id`, `method`, `result`, `confidence`. | Ver sección 4. |
| `cross_source_comparisons` | array de objetos | Comparaciones con otras fuentes (mismo cliente, contexto histórico). Cada comparación tiene `comparison_id`, `source_a`, `source_b`, `matches`, `discrepancies`. | Ver sección 5. |
| `hard_core_inferences` | array de objetos | Inferencias producidas por el Hard Core (motor determinista) a partir de hechos validados. Cada inferencia tiene `inference_id`, `input_facts`, `rule_applied`, `output`, `confidence`. | Ver sección 6. |
| `owner_decision_link` | string (opcional) | Referencia al DecisionRecord (Owner) que tomó una decisión final basada en esta cadena. Si está presente, vincula evidencia → decisión explícita. | `"decision_550e8400-e29b-41d4-a716-446655440000"` |
| `hashes` | objeto | Hash SHA-256 de cada componente de la cadena: `payload_hash`, `evidence_hash`, `facts_hash`, `inferences_hash`. | `{"payload_hash": "abc123...", "evidence_hash": "def456..."}` |
| `timestamps` | objeto | Fechas ISO 8601 de cada paso: `created_at`, `evidence_extracted_at`, `facts_extracted_at`, `validated_at`, `inferred_at`. | `{"created_at": "2026-05-05T11:00:00Z", ...}` |
| `confidence` | float (0.0–1.0) | Confianza agregada de toda la cadena, calculada como el producto ponderado de las confianzas de validación. | `0.89` |

---

## 2. primary_evidence

Cada elemento del array `primary_evidence` debe contener:

```json
{
  "type": "document_ocr",
  "content": "Texto extraído o referencia al binario.",
  "extracted_at": "2026-05-05T11:00:00Z",
  "extracted_by": "soft_core_module_v1",
  "confidence": 0.95
}
```

Tipos permitidos: `document_ocr`, `structured_form`, `api_response`, `email_thread`, `chat_log`, `manual_entry`.

Regla: `confidence` ≥ 0.5; si es menor, se debe generar un `validation` con resultado `LOW_CONFIDENCE`.

---

## 3. extracted_facts

Cada hecho extraído debe enlazarse a al menos una evidencia primaria.

```json
{
  "fact_id": "fact_001",
  "description": "El cliente presenta un saldo pendiente de $10.000.",
  "source_evidence_index": 0,
  "validated": false
}
```

- `validated` debe ser `false` inicialmente; solo pasa a `true` después de una validación exitosa.
- `source_evidence_index` es el índice en el array `primary_evidence`.

---

## 4. validations

Cada validación debe referenciar un `fact_id` y especificar el método usado.

```json
{
  "validation_id": "val_001",
  "fact_id": "fact_001",
  "method": "cross_source_check",
  "result": "PASS",
  "confidence": 0.98
}
```

Métodos permitidos: `cross_source_check`, `business_rule`, `temporal_consistency`, `external_api_verification`.

Resultados permitidos: `PASS`, `FAIL`, `INCONCLUSIVE`.

---

## 5. cross_source_comparisons

Solo se incluye si hay más de una fuente para el mismo cliente.

```json
{
  "comparison_id": "comp_001",
  "source_a": "evidence_chain_abc",
  "source_b": "evidence_chain_def",
  "matches": ["fact_001", "fact_002"],
  "discrepancies": [
    {
      "fact_id": "fact_003",
      "value_a": "100",
      "value_b": "200"
    }
  ]
}
```

---

## 6. hard_core_inferences

Cada inferencia debe listar los `input_facts` y la regla aplicada.

```json
{
  "inference_id": "inf_001",
  "input_facts": ["fact_001", "fact_002"],
  "rule_applied": "saldo_pendiente_mayor_umbral",
  "output": "ALERTA_SALDO_CRITICO",
  "confidence": 0.87
}
```

Reglas: definidas en el catálogo de reglas del Hard Core.  
Confianza: producto de las confianzas de los hechos de entrada, ajustado por la confianza de la regla.

---

## 7. Invariantes

### 7.1. *Ningún dato sin fuente*
Cada `fact_id` debe tener al menos un `source_evidence_index`. No se permite crear hechos de la nada.

### 7.2. *tenant_id prohibido*
El campo `tenant_id` no debe existir en la cadena. La segregación de clientes se realiza mediante `cliente_id`. El sistema no maneja multi‑tenant a nivel de infraestructura.

### 7.3. *Evidencia no es decisión*
La cadena de evidencia nunca debe contener un campo `decision` ni `owner_decision`. La decisión pertenece a la capa Owner (DecisionRecord) y se vincula mediante `owner_decision_link` (opcional).

### 7.4. *Inferencia no es hallazgo confirmado*
Una `hard_core_inference` no se considera un hallazgo confirmado hasta que un Owner (humano o sistema autorizado) la adopte como base de una decisión registrada.

### 7.5. *Toda decisión requiere Owner/DecisionRecord*
Si la cadena produce una salida que implica una acción operativa (crear job, enviar notificación, bloquear cuenta), debe existir un DecisionRecord referenciado en `owner_decision_link`. El sistema no ejecuta acciones automáticas sin registro explícito.

---

## 8. Ejemplo de cadena completa

```json
{
  "evidence_chain_id": "ec_550e8400-e29b-41d4-a716-446655440000",
  "cliente_id": "cliente_acme_sa",
  "source_payload_id": "pay_550e8400-e29b-41d4-a716-446655440000",
  "primary_evidence": [...],
  "extracted_facts": [...],
  "validations": [...],
  "cross_source_comparisons": [...],
  "hard_core_inferences": [...],
  "owner_decision_link": "decision_550e8400-e29b-41d4-a716-446655440000",
  "hashes": {...},
  "timestamps": {...},
  "confidence": 0.89
}
```

---

## 9. Ubicación en el flujo SmartPyme

- **Capa 0 (Canal Entrada Cruda):** genera `source_payload_id`.
- **Capa 01 (Normalización Documental):** produce `primary_evidence`.
- **Capa 02 (Actividad de Conocimiento):** extrae `extracted_facts`.
- **Capa 03 (Validación Operativa):** produce `validations` y `cross_source_comparisons`.
- **Hard Core (Motor Determinista):** genera `hard_core_inferences`.
- **Capa Owner (DecisionRecord):** consume la cadena y crea `owner_decision_link`.
