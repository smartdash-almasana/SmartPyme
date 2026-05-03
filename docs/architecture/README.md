# Arquitectura SmartPyme

## Estado

Índice rector de documentación arquitectónica.

Este archivo define el orden documental vigente para SmartPyme y evita ambigüedad entre documentos históricos, documentos especializados y documentos canónicos futuros.

## Regla de autoridad documental

Los documentos canónicos mandan sobre documentos históricos o especializados.

Los documentos antiguos no se borran automáticamente. Primero se clasifican como:

```text
KEEP
UPDATE
MERGE
SUPERSEDED
DEPRECATE
```

Cuando un documento sea absorbido por otro, debe quedar marcado como `SUPERSEDED` o `DEPRECATED` con referencia explícita al documento vigente.

## Documentos canónicos propuestos

La estructura documental objetivo es:

```text
SMARTPYME_ARCHITECTURE_MASTER.md
ADMISSION_AND_INTERACTION_MODEL.md
INVESTIGATIVE_METHODOLOGY.md
KNOWLEDGE_ARCHITECTURE.md
OPERATIONAL_CONTRACTS.md
PYME_DOMAIN_ATLAS.md
```

### 1. SMARTPYME_ARCHITECTURE_MASTER.md

Documento maestro del sistema.

Debe contener la visión global, principios de ingeniería, capas principales, ontología operativa, separación core/dominio, multiusuario y estrategia de producto.

### 2. ADMISSION_AND_INTERACTION_MODEL.md

Documento canónico futuro para admisión, anamnesis, inteligencia epistemológica, interacción con el dueño, ROI y construcción inicial del caso.

Hasta su consolidación, la fuente vigente es:

```text
SMARTPYME_ADMISSION_LAYER_V3.md
```

### 3. INVESTIGATIVE_METHODOLOGY.md

Documento canónico futuro para el método dual:

```text
mayéutica externa
+
hipotético-deductivo interno
```

Debe fusionar y ordenar:

```text
CONVERSATIONAL_METHODS.md
HYPOTHETICO_DEDUCTIVE_METHOD.md
```

### 4. KNOWLEDGE_ARCHITECTURE.md

Documento canónico futuro para conocimiento modular:

```text
Knowledge Tanks
Domain Packs
fuentes externas
APIs / MCP
```

Debe fusionar y ordenar:

```text
DOMAIN_PACK_ARCHITECTURE.md
KNOWLEDGE_TANKS_ARCHITECTURE.md
```

### 5. OPERATIONAL_CONTRACTS.md

Documento canónico futuro para contratos operativos:

```text
OperationalCase
DiagnosticReport
ValidatedCaseRecord
DecisionRecord
EvidenceItem
EvidenceTask
```

Hasta su consolidación, la fuente vigente es:

```text
OPERATIONAL_CASE_AND_REPORTS.md
```

### 6. PYME_DOMAIN_ATLAS.md

Documento canónico futuro para contenido específico del dominio PyME:

```text
síntomas
patologías
modelos operativos
skills candidatas
evidencias requeridas
preguntas mayéuticas
criterios de avance y bloqueo
```

Debe fusionar y ordenar:

```text
SYMPTOM_PATHOLOGY_CATALOG_DESIGN.md
PYME_SYMPTOM_PATHOLOGY_ATLAS.md
PYME_OPERATIONAL_MODELS_SYMPTOMS_AND_CASES.md
```

## Estado transitorio vigente

Mientras se consolidan los documentos canónicos, usar estas fuentes:

| Área | Fuente vigente transitoria |
|---|---|
| Admisión, anamnesis, epistemología, ROI | `SMARTPYME_ADMISSION_LAYER_V3.md` |
| Visión global | `SMARTPYME_ARCHITECTURE_MASTER.md` |
| Método conversacional | `CONVERSATIONAL_METHODS.md` |
| Método interno | `CONVERSATIONAL_METHODS.md`; `HYPOTHETICO_DEDUCTIVE_METHOD.md` queda como candidato a merge |
| Catálogo síntoma-patología | `SYMPTOM_PATHOLOGY_CATALOG_DESIGN.md` |
| Casos y reportes | `OPERATIONAL_CASE_AND_REPORTS.md` |
| Conocimiento modular | `DOMAIN_PACK_ARCHITECTURE.md` + `KNOWLEDGE_TANKS_ARCHITECTURE.md` |
| Atlas PyME | `PYME_SYMPTOM_PATHOLOGY_ATLAS.md` + `PYME_OPERATIONAL_MODELS_SYMPTOMS_AND_CASES.md` |

## Orden de lectura recomendado

Para agentes, desarrolladores o auditores:

1. `SMARTPYME_ARCHITECTURE_MASTER.md`
2. `SMARTPYME_ADMISSION_LAYER_V3.md`
3. `CONVERSATIONAL_METHODS.md`
4. `SYMPTOM_PATHOLOGY_CATALOG_DESIGN.md`
5. `OPERATIONAL_CASE_AND_REPORTS.md`
6. `DOMAIN_PACK_ARCHITECTURE.md`
7. `KNOWLEDGE_TANKS_ARCHITECTURE.md`
8. `PYME_SYMPTOM_PATHOLOGY_ATLAS.md`
9. `PYME_OPERATIONAL_MODELS_SYMPTOMS_AND_CASES.md`

## Principios arquitectónicos vigentes

1. SmartPyme no inventa: clasifica, recupera, calcula y valida.
2. El dueño es la primera fuente de conocimiento.
3. La primera capa es anamnesis/admisión, no respuesta rápida.
4. Secuencia rectora inicial:

```text
Dueño → Anamnesis → Taxonomía → Variables base → Demanda → Caso
```

5. La evidencia tiene estado epistemológico:

```text
CERTEZA / DUDA / DESCONOCIMIENTO
```

6. La DUDA genera tarea con responsable, formato y tiempo.
7. ROI gobierna prioridad:

```text
SANGRIA > INESTABILIDAD > OPTIMIZACION
```

8. El catálogo de patologías clasifica.
9. El Knowledge Tank contiene fórmulas y métodos.
10. El caso operativo conecta demanda, patología, evidencia y fórmula.
11. La admisión no diagnostica ni ejecuta fórmula final.
12. Cada ciclo se cierra o refrenda con el dueño.
13. El diagnóstico final es una coordenada de salud operativa, no una lista suelta de problemas.

## Próximos refactors documentales

### DOC_REFACTOR_002

Reformatear `SMARTPYME_ARCHITECTURE_MASTER.md`.

Motivo: auditoría documental detectó que el archivo puede estar en una sola línea o con formato difícil de leer para agentes y humanos.

### DOC_REFACTOR_003

Fusionar:

```text
CONVERSATIONAL_METHODS.md
HYPOTHETICO_DEDUCTIVE_METHOD.md
```

en:

```text
INVESTIGATIVE_METHODOLOGY.md
```

### DOC_REFACTOR_004

Fusionar:

```text
DOMAIN_PACK_ARCHITECTURE.md
KNOWLEDGE_TANKS_ARCHITECTURE.md
```

en:

```text
KNOWLEDGE_ARCHITECTURE.md
```

### DOC_REFACTOR_005

Consolidar:

```text
SYMPTOM_PATHOLOGY_CATALOG_DESIGN.md
PYME_SYMPTOM_PATHOLOGY_ATLAS.md
PYME_OPERATIONAL_MODELS_SYMPTOMS_AND_CASES.md
```

en:

```text
PYME_DOMAIN_ATLAS.md
```

### DOC_REFACTOR_006

Actualizar `OPERATIONAL_CASE_AND_REPORTS.md` para incorporar explícitamente:

```text
domain_id
estado epistemológico de evidencia
relación con EvidenceTask
```

## Política anti-caos documental

No crear nuevos documentos conceptuales sin:

1. definir capa lógica;
2. indicar relación con documentos existentes;
3. declarar si reemplaza, amplía o especializa otro documento;
4. registrar siguiente paso de implementación o validación.

Objetivo:

```text
cosmos después del caos
```
