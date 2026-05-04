# SmartPyme — Capa 1.5: Normalización Documental, Entidades y Tiempo

## Estado

DOCUMENTO RECTOR — CANÓNICO

**Versión:** 1.0  
**Fecha:** Mayo 2026  
**Origen:** Derivado y expandido desde `SMARTPYME_CAPA_015_CONCEPTO_CLAVE_NORMALIZACION_ENTIDADES_TIEMPO.md`  
**Uso:** Interno — Equipo de Producto SmartPyme

---

## Posición en la arquitectura

```text
Capa 1   → Admisión Epistemológica       → produce InitialCaseAdmission
Capa 1.5 → Normalización Documental,
           Entidades y Tiempo            → produce NormalizedEvidencePackage
Capa 2   → Activación de Conocimiento
           e Investigación               → consume variables limpias
```

La Capa 1.5 es la frontera entre el mundo humano y el mundo investigable.

Sin ella, el sistema investiga sobre ruido.

---

## 0. Principios rectores de la capa

```text
Sin tiempo no hay variable investigable.
Sin entidad canónica no hay comparación confiable.
Sin fuente trazable no hay hallazgo.
La evidencia cruda no se investiga directamente.
Capa 1.5 no diagnostica: prepara evidencia.
Capa 2 no debe operar sobre documentos crudos.
```

---

## 1. Problema que resuelve

Después de la admisión, SmartPyme ya sabe:

- qué dijo el dueño;
- qué duele;
- qué fase clínica corresponde;
- qué evidencia existe, falta o está en duda;
- quién podría tener esa evidencia;
- qué tareas hay que generar.

Pero todavía no puede investigar.

La evidencia cruda no llega limpia. Llega como:

- Excel con columnas ambiguas (`prov.`, `cant.`, `$`, `fecha?`);
- PDFs con nombres de entidades inconsistentes;
- WhatsApps informales con datos mezclados;
- proveedores escritos de múltiples maneras;
- productos con abreviaturas o sin código;
- fechas incompletas, ambiguas o ausentes;
- datos de distintos períodos mezclados en la misma hoja;
- columnas sin encabezado o con encabezados duplicados.

Si el sistema investiga directamente sobre esa evidencia sin normalizarla, produce:

- comparaciones entre períodos distintos;
- entidades duplicadas contadas como distintas;
- variables sin fuente trazable;
- hallazgos falsos o no reproducibles.

La Capa 1.5 resuelve ese problema antes de que llegue a la investigación.

---

## 2. Qué entra desde Capa 1

La Capa 1 produce un `InitialCaseAdmission` que contiene:

- demanda ordenada del dueño;
- personas detectadas como nodos de acceso;
- fuentes probables identificadas;
- evidencias clasificadas como CERTEZA, DUDA o DESCONOCIMIENTO;
- tareas de evidencia pendientes;
- fase clínica detectada;
- síntomas candidatos;
- patologías candidatas.

Cuando las tareas de evidencia se ejecutan y los documentos empiezan a llegar, la Capa 1.5 los recibe.

El `InitialCaseAdmission` actúa como contexto de referencia: dice qué se esperaba, de quién y para qué hipótesis.

---

## 3. Qué evidencia y documentos recibe

La Capa 1.5 puede recibir cualquier tipo de documento o fuente de datos:

| Tipo | Ejemplos |
|---|---|
| Planillas | Excel, Google Sheets, CSV |
| Documentos | PDF, Word, facturas escaneadas |
| Mensajes | WhatsApp exportado, Telegram, email |
| Imágenes | Capturas de pantalla, fotos de libreta |
| Reportes | Exportaciones de sistemas POS, ERP, facturación |
| Texto libre | Listas dictadas, notas del dueño |
| Datos estructurados | JSON, XML de sistemas externos |

Cada documento recibido se registra como `RawDocument` antes de cualquier procesamiento.

---

## 4. Qué hace con columnas, entidades, aliases y fuentes

### 4.1 Columnas

Los documentos tienen columnas que pueden significar lo mismo con nombres distintos.

Ejemplos de ambigüedad real:

```text
"Proveedor" / "prov." / "Nombre proveedor" / "Razón social" / "Vendedor"
"Cantidad" / "cant." / "Unidades" / "Q" / "Qty"
"Precio" / "P.U." / "Precio unitario" / "$" / "Valor"
"Fecha" / "Fecha venta" / "Día" / "Fecha emisión" / "F."
```

La Capa 1.5 no asume equivalencias automáticamente.

Produce `ColumnCandidate` para cada columna relevante:

```text
ColumnCandidate:
  raw_column: "prov."
  possible_meaning: "proveedor"
  confidence: 0.78
  requires_confirmation: true
  source_document_id: doc_excel_paulita_001
```

Las columnas con confianza baja o ambigüedad alta se marcan para confirmación.

Las columnas irrelevantes se descartan con trazabilidad.

---

### 4.2 Entidades

Una entidad es cualquier objeto de negocio que puede ser observado, comparado o medido.

Ejemplos:

```text
producto / SKU / artículo
proveedor / razón social
cliente
empleado
venta / transacción
compra / orden de compra
factura
cuenta bancaria
caja / caja chica
sucursal / depósito
documento / expediente
```

El problema central es que las entidades no siempre aparecen con el mismo nombre en distintos documentos o incluso dentro del mismo documento.

Ejemplo real:

```text
"Textiles San Martín"
"Textil San Martin"
"TSM"
"San Martín Textil"
"Proveedor San Martin"
"T. San Martín"
```

Pueden ser la misma entidad o no.

La Capa 1.5 detecta menciones (`EntityMention`) y las agrupa bajo una entidad canónica (`CanonicalEntity`) con sus aliases.

---

### 4.3 Aliases

Los aliases son los nombres alternativos con los que una entidad aparece en los documentos.

La entidad canónica no borra los nombres originales.

Los conserva como aliases trazables para que cualquier hallazgo pueda rastrearse hasta la fuente original.

```text
CanonicalEntity:
  entity_id: proveedor_textiles_san_martin
  entity_type: proveedor
  canonical_name: "Textiles San Martín"
  aliases:
    - EntityAlias(raw_name="Textil San Martin", source="excel_paulita", confidence=0.91)
    - EntityAlias(raw_name="TSM", source="factura_proveedor_003", confidence=0.74)
    - EntityAlias(raw_name="San Martín Textil", source="whatsapp_dueño", confidence=0.85)
  sources:
    - excel_paulita
    - factura_proveedor_003
    - whatsapp_dueño
  confidence: 0.86
  requires_confirmation: false
```

---

### 4.4 Fuentes

Cada variable, entidad y columna debe mantener referencia a su fuente original.

La `EvidenceReference` vincula una variable limpia con el documento y la celda o fragmento exacto de donde proviene.

```text
EvidenceReference:
  evidence_ref_id: ref_001
  source_document_id: doc_excel_paulita_001
  source_field: "cant."
  source_row: 14
  source_sheet: "Stock_Mayo"
  raw_value: "120"
  normalized_value: 120
  unit: "unidades"
```

Sin esta referencia, el hallazgo no es trazable.

Sin trazabilidad, el hallazgo no es válido.

---

## 5. Por qué toda variable necesita tiempo

Una variable sin dimensión temporal no es investigable.

Ejemplos del problema:

```text
stock_actual          → ¿de qué fecha?
precio_actual         → ¿vigente desde cuándo?
ventas                → ¿de qué período?
gastos                → ¿de qué período?
costo_reposicion      → ¿actualizado cuándo?
proveedor_activo      → ¿activo durante qué período?
```

Sin tiempo, el sistema puede comparar:

```text
ventas de abril
contra gastos de marzo
contra stock de hoy
contra precios de hace seis meses
```

Eso produce diagnósticos falsos.

El tiempo no es un campo opcional. Es una condición de existencia de la variable.

Regla:

```text
Si una variable no tiene ventana temporal asignable, no puede ser usada en investigación.
Debe marcarse como TEMPORAL_UNKNOWN y bloquearse hasta resolución.
```

---

## 6. TemporalWindow

Cada evidencia y cada variable debe tener una `TemporalWindow` cuando aplique.

La ventana temporal tiene cinco campos:

### observed_at

Fecha en que el dato fue observado, registrado o capturado.

Aplica a: snapshots, inventarios físicos, precios puntuales, saldos de caja.

```text
stock_actual:
  observed_at: 2026-05-03
```

### period_start / period_end

Período que cubre un dato acumulado o agregado.

Aplica a: ventas del mes, gastos del trimestre, compras del período.

```text
ventas_abril:
  period_start: 2026-04-01
  period_end: 2026-04-30
```

### valid_from / valid_to

Vigencia de un precio, condición comercial, regla o acuerdo.

`valid_to: null` significa vigente hasta nuevo aviso.

```text
precio_lista_pantalon_x:
  valid_from: 2026-04-15
  valid_to: null
```

### Combinaciones válidas

| Tipo de dato | Campos requeridos |
|---|---|
| Snapshot puntual | `observed_at` |
| Dato acumulado | `period_start` + `period_end` |
| Precio o condición vigente | `valid_from` (+ `valid_to` si venció) |
| Dato histórico con vigencia | `valid_from` + `valid_to` |
| Dato sin tiempo conocido | `TEMPORAL_UNKNOWN` → bloqueo |

---

## 7. Objetos conceptuales

La Capa 1.5 introduce los siguientes objetos. Son conceptuales en este documento. Los contratos Python se definen en la tarea siguiente.

---

### RawDocument

Documento recibido tal como llegó, sin modificar.

```text
RawDocument:
  raw_document_id       identificador único
  cliente_id            tenant
  case_id               caso de admisión al que pertenece
  evidence_item_id      referencia al EvidenceItem de Capa 1
  filename              nombre original del archivo
  file_type             xlsx / pdf / txt / image / json / otro
  received_at           timestamp de recepción
  received_from         person_id o canal de origen
  file_hash             hash SHA-256 para integridad
  size_bytes            tamaño
  raw_content_ref       referencia al contenido almacenado
  processing_status     PENDING / IN_PROGRESS / DONE / BLOCKED
  notes                 observaciones
```

---

### DocumentSchema

Esquema detectado en el documento: columnas, tipos, estructura.

```text
DocumentSchema:
  schema_id             identificador único
  raw_document_id       documento de origen
  detected_columns      lista de ColumnCandidate
  detected_entity_types tipos de entidades detectadas
  row_count             filas detectadas
  has_header            booleano
  sheet_name            nombre de hoja si aplica
  detection_confidence  confianza general del esquema
  ambiguities           lista de alertas de ambigüedad
  schema_status         CLEAN / AMBIGUOUS / BLOCKED
```

---

### ColumnCandidate

Columna detectada en un documento con su posible significado semántico.

```text
ColumnCandidate:
  column_candidate_id   identificador único
  schema_id             esquema de origen
  raw_column            nombre original de la columna
  possible_meaning      significado semántico candidato
  data_type             string / number / date / boolean / mixed
  sample_values         muestra de valores reales
  confidence            0.0 a 1.0
  requires_confirmation booleano
  confirmed_by          person_id si fue confirmada manualmente
  status                CANDIDATE / CONFIRMED / DISCARDED / AMBIGUOUS
```

---

### EntityMention

Mención de una entidad tal como aparece en el documento, antes de resolución canónica.

```text
EntityMention:
  mention_id            identificador único
  raw_document_id       documento de origen
  raw_value             texto original: "TSM", "Textil San Martin"
  entity_type_candidate tipo probable: proveedor / producto / cliente
  source_field          columna o campo de origen
  source_row            fila de origen
  confidence            0.0 a 1.0
  resolution_status     PENDING / RESOLVED / UNRESOLVABLE
  canonical_entity_id   referencia si ya fue resuelta
```

---

### CanonicalEntity

Entidad normalizada con nombre canónico y aliases trazables.

```text
CanonicalEntity:
  entity_id             identificador único
  cliente_id            tenant
  entity_type           proveedor / producto / cliente / empleado / otro
  canonical_name        nombre canónico elegido
  aliases               lista de EntityAlias
  sources               lista de raw_document_id que la mencionan
  confidence            0.0 a 1.0
  requires_confirmation booleano
  confirmed_by          person_id si fue confirmada manualmente
  created_at            timestamp
  updated_at            timestamp
```

---

### EntityAlias

Nombre alternativo de una entidad canónica, con trazabilidad a su fuente.

```text
EntityAlias:
  alias_id              identificador único
  canonical_entity_id   entidad canónica a la que pertenece
  raw_name              nombre original: "TSM"
  source_document_id    documento donde apareció
  source_field          campo o columna de origen
  confidence            0.0 a 1.0
```

---

### SourceFieldMapping

Mapeo entre un campo crudo del documento y un campo semántico canónico del sistema.

```text
SourceFieldMapping:
  mapping_id            identificador único
  schema_id             esquema de origen
  raw_column            nombre original: "prov."
  canonical_field       nombre canónico: "proveedor"
  canonical_field_type  tipo semántico del campo canónico
  confidence            0.0 a 1.0
  requires_confirmation booleano
  confirmed_by          person_id si fue confirmada manualmente
  status                CANDIDATE / CONFIRMED / DISCARDED
```

---

### EvidenceReference

Referencia trazable que vincula una variable limpia con su origen exacto en el documento.

```text
EvidenceReference:
  evidence_ref_id       identificador único
  source_document_id    documento de origen
  source_field          columna o campo original
  source_row            fila de origen (si aplica)
  source_sheet          hoja de origen (si aplica)
  raw_value             valor original sin modificar
  normalized_value      valor después de normalización
  unit                  unidad si aplica
  transformation_notes  qué se hizo para normalizar
```

---

### TemporalWindow

Ventana temporal de una variable o evidencia.

```text
TemporalWindow:
  window_id             identificador único
  observed_at           fecha de observación puntual (opcional)
  period_start          inicio del período cubierto (opcional)
  period_end            fin del período cubierto (opcional)
  valid_from            inicio de vigencia (opcional)
  valid_to              fin de vigencia, null si sigue vigente (opcional)
  temporal_status       KNOWN / PARTIAL / UNKNOWN
  resolution_notes      cómo se determinó la ventana
```

---

### CleanVariable

Variable investigable: limpia, trazable, con entidad canónica y ventana temporal.

```text
CleanVariable:
  variable_id           identificador único
  cliente_id            tenant
  case_id               caso de admisión
  variable_type         stock / precio / venta / gasto / costo / otro
  entity_id             entidad canónica a la que aplica
  value                 valor numérico o categórico
  unit                  unidad de medida
  evidence_ref_id       referencia a EvidenceReference
  temporal_window       TemporalWindow asociada
  confidence            0.0 a 1.0
  curation_status       CLEAN / NEEDS_REVIEW / BLOCKED
  notes                 observaciones
```

---

### NormalizedEvidencePackage

Output de la Capa 1.5. Paquete completo de evidencia normalizada listo para Capa 2.

```text
NormalizedEvidencePackage:
  package_id            identificador único
  cliente_id            tenant
  case_id               caso de admisión de origen
  created_at            timestamp de creación
  raw_documents         lista de RawDocument procesados
  schemas               lista de DocumentSchema detectados
  column_candidates     lista de ColumnCandidate
  entity_mentions       lista de EntityMention
  canonical_entities    lista de CanonicalEntity
  source_field_mappings lista de SourceFieldMapping
  evidence_references   lista de EvidenceReference
  clean_variables       lista de CleanVariable
  temporal_windows      lista de TemporalWindow
  ambiguity_alerts      lista de alertas de ambigüedad pendientes
  package_status        READY / PARTIAL / BLOCKED
  blocking_reasons      lista de razones de bloqueo si aplica
  next_step             instrucción para Capa 2 o para el dueño
```

---

## 8. Qué produce

El output exclusivo de la Capa 1.5 es un `NormalizedEvidencePackage`.

Este paquete puede tener tres estados:

### READY

Todos los documentos fueron procesados, las entidades resueltas, las columnas mapeadas y las variables tienen ventana temporal.

Capa 2 puede operar.

### PARTIAL

Algunos documentos fueron procesados pero quedan ambigüedades o variables sin tiempo.

Capa 2 puede operar sobre las variables limpias disponibles, con alcance limitado.

Las ambigüedades se registran como alertas y se devuelven al dueño para confirmación.

### BLOCKED

No hay suficiente evidencia normalizada para investigar.

El sistema devuelve al dueño con una pregunta mayéutica concreta sobre qué falta.

---

## 9. Relación con Capa 2

La Capa 2 — Activación de Conocimiento e Investigación — necesita variables limpias para:

- activar fórmulas del Knowledge Tank;
- comparar valores contra referencias o benchmarks;
- detectar diferencias cuantificadas;
- producir hallazgos trazables.

La Capa 2 no debe recibir documentos crudos.

La Capa 2 no debe resolver entidades ni columnas.

La Capa 2 no debe inferir períodos.

Todo eso es responsabilidad de la Capa 1.5.

La interfaz entre capas es el `NormalizedEvidencePackage`.

```text
Capa 1.5 produce:  NormalizedEvidencePackage
Capa 2 consume:    NormalizedEvidencePackage.clean_variables
                   NormalizedEvidencePackage.canonical_entities
                   NormalizedEvidencePackage.temporal_windows
```

---

## 10. Ejemplo completo — Excel de Paulita

### Contexto

Capa 1 detectó:

```text
EvidenceItem:
  evidence_type: Excel_stock
  epistemic_state: DUDA
  responsible_person_id: person_paulita
```

El dueño envió el archivo. Llega a Capa 1.5.

---

### Paso 1 — RawDocument

```text
RawDocument:
  raw_document_id: doc_excel_paulita_001
  filename: "stock_mayo_paulita.xlsx"
  file_type: xlsx
  received_at: 2026-05-03T14:22:00Z
  received_from: person_paulita
  processing_status: PENDING
```

---

### Paso 2 — DocumentSchema

El sistema detecta las columnas del Excel:

```text
DocumentSchema:
  schema_id: schema_001
  raw_document_id: doc_excel_paulita_001
  detected_columns:
    - raw_column: "prov."
    - raw_column: "producto"
    - raw_column: "cant."
    - raw_column: "precio"
    - raw_column: "fecha"
  row_count: 87
  has_header: true
  sheet_name: "Stock_Mayo"
  schema_status: AMBIGUOUS
  ambiguities:
    - "prov. podría ser proveedor o vendedor"
    - "fecha no tiene año explícito en 12 filas"
```

---

### Paso 3 — ColumnCandidate

```text
ColumnCandidate:
  raw_column: "prov."
  possible_meaning: "proveedor"
  confidence: 0.78
  requires_confirmation: true

ColumnCandidate:
  raw_column: "cant."
  possible_meaning: "cantidad"
  confidence: 0.95
  requires_confirmation: false

ColumnCandidate:
  raw_column: "precio"
  possible_meaning: "precio_unitario"
  confidence: 0.88
  requires_confirmation: false

ColumnCandidate:
  raw_column: "fecha"
  possible_meaning: "observed_at"
  confidence: 0.71
  requires_confirmation: true
```

---

### Paso 4 — EntityMention y CanonicalEntity

El sistema detecta menciones de productos:

```text
EntityMention:
  raw_value: "PJ-AZ-42"
  entity_type_candidate: producto
  source_field: "producto"
  source_row: 14
  confidence: 0.82

CanonicalEntity:
  entity_id: producto_pantalon_jean_azul_talle_42
  entity_type: producto
  canonical_name: "Pantalón jean azul talle 42"
  aliases:
    - EntityAlias(raw_name="PJ-AZ-42", source="doc_excel_paulita_001", confidence=0.82)
    - EntityAlias(raw_name="jean azul 42", source="doc_excel_paulita_001", confidence=0.79)
  confidence: 0.82
  requires_confirmation: true
```

---

### Paso 5 — TemporalWindow

La columna `fecha` tiene valores pero sin año en 12 filas.

```text
TemporalWindow:
  observed_at: 2026-05-03
  period_start: null
  period_end: null
  temporal_status: PARTIAL
  resolution_notes: "12 filas sin año. Se asume 2026 por contexto de recepción."
```

---

### Paso 6 — CleanVariable

```text
CleanVariable:
  variable_id: stock_pantalon_jean_azul_talle_42
  variable_type: stock
  entity_id: producto_pantalon_jean_azul_talle_42
  value: 120
  unit: unidades
  evidence_ref_id: ref_fila_14_excel_paulita
  temporal_window:
    observed_at: 2026-05-03
    temporal_status: PARTIAL
  confidence: 0.82
  curation_status: NEEDS_REVIEW
```

---

### Paso 7 — NormalizedEvidencePackage

```text
NormalizedEvidencePackage:
  package_id: pkg_perales_001
  case_id: case_perales_001
  package_status: PARTIAL
  clean_variables: [stock_pantalon_jean_azul_talle_42, ...]
  ambiguity_alerts:
    - "Columna 'prov.' requiere confirmación: ¿es proveedor o vendedor?"
    - "12 filas sin año en columna 'fecha'. Se asumió 2026."
    - "Entidades de producto requieren confirmación de nombres canónicos."
  next_step: "Confirmar si 'prov.' es proveedor o vendedor, y validar nombres de productos."
```

---

## 11. Reglas rectoras

1. La evidencia cruda no se investiga directamente.
2. Todo documento recibido debe registrarse como `RawDocument` antes de cualquier procesamiento.
3. Todo documento debe producir un `DocumentSchema` o un bloqueo documentado.
4. Toda columna relevante debe mapearse con `SourceFieldMapping` o marcarse como ambigua.
5. Toda entidad debe conservar sus aliases originales en `EntityAlias`.
6. Toda variable debe tener una `EvidenceReference` trazable a su fuente exacta.
7. Toda variable debe tener una `TemporalWindow` o marcarse como `TEMPORAL_UNKNOWN`.
8. Sin entidad canónica no hay comparación confiable.
9. Sin tiempo no hay variable investigable.
10. Sin fuente trazable no hay hallazgo.
11. La ambigüedad no se oculta: se registra como alerta y se devuelve al dueño.
12. Capa 1.5 no diagnostica: prepara evidencia.
13. Capa 2 no debe operar sobre documentos crudos.
14. Un `NormalizedEvidencePackage` en estado `BLOCKED` no habilita investigación.
15. La confirmación manual de entidades y columnas es válida y trazable.

---

## 12. Diferencia entre Capa 1.5 y curación de datos existente

El sistema ya tiene un `DataCurationService` que valida presencia, estructura, dominio y relevancia de datos individuales.

La Capa 1.5 opera en un nivel superior:

| Dimensión | DataCurationService | Capa 1.5 |
|---|---|---|
| Unidad de trabajo | Campo o valor individual | Documento completo |
| Pregunta que responde | ¿Este dato es válido? | ¿De qué entidad es este dato y en qué período? |
| Output | Dato curado o rechazado | Variable investigable con entidad y tiempo |
| Relación con entidades | No resuelve entidades | Resuelve y canonicaliza entidades |
| Relación con tiempo | No gestiona períodos | Asigna TemporalWindow a cada variable |
| Relación con fuentes | Valida el dato | Traza el dato hasta su celda de origen |

Ambas capas son necesarias y complementarias.

---

## 13. Fórmula conceptual final

```text
Documento crudo
+ columnas detectadas y mapeadas
+ entidades canónicas con aliases
+ fuente trazable por celda
+ ventana temporal asignada
= variable investigable
```

```text
Variables investigables
+ entidades canónicas
+ ventanas temporales
+ referencias de evidencia
= NormalizedEvidencePackage
```

```text
NormalizedEvidencePackage (READY o PARTIAL)
→ habilita Capa 2
```

---

## 14. Qué no hace esta capa

La Capa 1.5 no:

- diagnostica;
- calcula fórmulas de negocio;
- emite hallazgos;
- propone acciones;
- crea `OperationalCase`;
- reemplaza la validación del dueño;
- inventa entidades sin evidencia;
- asume períodos sin base documental;
- oculta ambigüedades.

---

## 15. Próximo paso hacia contratos Python

La implementación de esta capa debe seguir el protocolo `PLAN → WRITE → VERIFY → INSPECT → RUN → REPORT`.

TaskSpec sugerida:

```text
TS_015_001_CONTRATOS_NORMALIZACION
```

Archivos objetivo:

```text
app/contracts/normalization_contract.py
tests/contracts/test_normalization_contract.py
```

Contratos mínimos a implementar en ese orden:

```python
# Tipos literales
NormalizationStatus = Literal["CLEAN", "NEEDS_REVIEW", "BLOCKED"]
TemporalStatus = Literal["KNOWN", "PARTIAL", "UNKNOWN"]
PackageStatus = Literal["READY", "PARTIAL", "BLOCKED"]
ColumnStatus = Literal["CANDIDATE", "CONFIRMED", "DISCARDED", "AMBIGUOUS"]
MappingStatus = Literal["CANDIDATE", "CONFIRMED", "DISCARDED"]
ResolutionStatus = Literal["PENDING", "RESOLVED", "UNRESOLVABLE"]
ProcessingStatus = Literal["PENDING", "IN_PROGRESS", "DONE", "BLOCKED"]

# Modelos
class TemporalWindow(BaseModel): ...
class EvidenceReference(BaseModel): ...
class EntityAlias(BaseModel): ...
class CanonicalEntity(BaseModel): ...
class EntityMention(BaseModel): ...
class ColumnCandidate(BaseModel): ...
class SourceFieldMapping(BaseModel): ...
class DocumentSchema(BaseModel): ...
class RawDocument(BaseModel): ...
class CleanVariable(BaseModel): ...
class NormalizedEvidencePackage(BaseModel): ...
```

Tests mínimos requeridos:

1. Construir `NormalizedEvidencePackage` válido.
2. `TemporalWindow` con todos los campos `null` debe tener `temporal_status = UNKNOWN`.
3. `CleanVariable` con `curation_status = BLOCKED` no debe tener `value` requerido.
4. `CanonicalEntity` conserva aliases originales.
5. `NormalizedEvidencePackage` en estado `BLOCKED` debe tener `blocking_reasons` no vacío.
6. `EvidenceReference` vincula `raw_value` con `normalized_value` trazablemente.
