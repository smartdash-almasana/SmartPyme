# SmartPyme — Tanques Específicos y Motor de Fuentes Idóneas

## Estado

Documento conceptual crítico.

Este documento consolida el diseño trabajado sobre los **tanques de conocimiento específicos por rubro** y su relación con un **motor externo de abastecimiento, descubrimiento, calificación y uso bajo demanda de fuentes idóneas**.

La idea principal:

```text
Cada tanque específico no debe nacer como una enciclopedia completa.
Debe nacer con estructura semántica, fuentes idóneas calificadas y capacidad de búsqueda bajo demanda.
```

Frase rectora:

```text
Fuente validada en reposo.
Conocimiento específico bajo demanda.
Promoción solo por curación.
```

---

# 1. Punto de partida

SmartPyme ya definió una arquitectura donde:

```text
El core opera.
Los tanques alimentan.
El dominio se arma combinando tanques.
```

El core conserva el método:

```text
recepción
→ conversación mayéutica
→ interpretación
→ curación
→ condiciones
→ hipótesis
→ caso operativo
→ investigación
→ reporte diagnóstico
→ propuesta
→ decisión registrada
→ autorización
→ acción controlada
→ trazabilidad
```

Los tanques aportan:

```text
síntomas
patologías
fórmulas
protocolos
variables
evidencias
benchmarks
buenas prácticas
preguntas mayéuticas
lenguaje del rubro
criterios de diagnóstico
criterios de impacto
skills especializadas
```

---

# 2. Nueva intuición

Cuando se crea un tanque específico, por ejemplo:

```text
tanque_agro
tanque_metalurgica
tanque_gastronomia
tanque_salud
tanque_construccion
tanque_software
```

no conviene pretender que ya tenga todo el conocimiento cargado manualmente.

El tanque debe tener tres cosas:

```text
1. estructura interna mínima;
2. mapa de fuentes idóneas;
3. capacidad de activar búsqueda externa cuando un caso lo requiera.
```

---

# 3. Diseño general

```text
Nuevo tanque específico
→ clasificación del dominio
→ búsqueda profunda de fuentes idóneas
→ ranking y calificación de fuentes
→ whitelist del tanque
→ conexión pasiva
→ activación bajo demanda por brecha de conocimiento
→ succión de conocimiento específico
→ filtro anti-basura
→ uso como referencia de caso
→ promoción al tanque solo si se valida
```

---

# 4. Dos modos del tanque

## 4.1 Modo pasivo

Cuando el tanque nace, no consulta permanentemente.

Primero prepara su mapa de fuentes.

Hace:

```text
- identifica organismos relevantes;
- identifica universidades;
- identifica bibliotecas técnicas;
- identifica APIs disponibles;
- identifica normas;
- identifica cámaras sectoriales;
- identifica manuales;
- identifica bases de datos públicas o privadas;
- clasifica temas cubiertos;
- asigna trust_level;
- registra forma de acceso;
- deja fuentes listas para uso futuro.
```

Ejemplo para `tanque_agro`:

```text
INTA
FAO
universidades agrarias
ministerios agropecuarios
cámaras agropecuarias
manuales técnicos
bases climáticas
documentación sobre suelos
fuentes sobre fertilización
fuentes sobre riego
fuentes sobre salinidad
fuentes sobre humedad de suelo
```

Resultado:

```text
El tanque queda conectado pasivamente.
No está lleno de datos basura.
Tiene una lista de fuentes confiables preparadas.
```

---

## 4.2 Modo activo

El modo activo se dispara solo cuando un caso lo requiere.

Ejemplo:

```text
Un agricultor consulta sobre humedad de tierra, salinidad, riego, rendimiento y costos por hectárea.
```

El sistema evalúa:

```text
¿Alcanza el tanque interno?
¿Falta evidencia del cliente?
¿Falta conocimiento técnico externo?
¿Qué fuente idónea ya está calificada para este tema?
```

Si falta conocimiento:

```text
KnowledgeGapDetector
→ SourceSelector
→ KnowledgeSourcePlugin
→ ExternalKnowledgeIntakeEngine
→ AntiGarbageFilter
→ Curator
→ ReferenceBundle
→ uso en OperationalCase / DiagnosticReport
```

---

# 5. Distinción crítica

```text
Brecha de evidencia ≠ brecha de conocimiento
```

## Brecha de evidencia

Falta información concreta del cliente.

Ejemplos:

```text
ventas del período;
facturas del proveedor;
extracto bancario;
inventario físico;
costos propios;
receta;
BOM;
análisis de suelo del campo;
mediciones propias.
```

Respuesta del sistema:

```text
pedir evidencia al dueño o usuario autorizado.
```

---

## Brecha de conocimiento

Falta saber técnico del dominio.

Ejemplos:

```text
qué variables aplicar para humedad de suelo;
qué protocolo usar para salinidad;
qué fórmula usar para margen bruto agropecuario;
qué norma aplicar en industria;
qué benchmark usar en logística;
qué indicador corresponde a turnos clínicos.
```

Respuesta del sistema:

```text
consultar fuentes idóneas calificadas.
```

---

## Regla

```text
La evidencia la aporta el cliente.
El conocimiento puede venir del tanque o de fuentes externas.
```

Y:

```text
La referencia externa orienta.
La evidencia del cliente prueba.
```

---

# 6. Nuevo componente: Knowledge Gap Detector

Nombre técnico:

```text
KnowledgeGapDetector
```

Nombre en castellano:

```text
Detector de Brecha de Conocimiento
```

Función:

```text
Determinar si el caso puede investigarse con conocimiento interno
o si requiere referencia externa específica.
```

---

## Contrato conceptual

```python
KnowledgeGapAssessment:
    assessment_id: str
    case_id: str
    tank_id: str
    required_knowledge: list[str]
    available_internal_knowledge: list[str]
    missing_knowledge: list[str]
    evidence_gaps: list[str]
    knowledge_gaps: list[str]
    external_lookup_required: bool
    candidate_sources: list[str]
    decision: "INTERNAL_SUFFICIENT" | "EVIDENCE_REQUIRED" | "EXTERNAL_KNOWLEDGE_REQUIRED" | "INSUFFICIENT_KNOWLEDGE"
    reason: str
```

---

## Decisiones posibles

```text
INTERNAL_SUFFICIENT:
El tanque interno alcanza para orientar o investigar.

EVIDENCE_REQUIRED:
No falta conocimiento; falta evidencia del cliente.

EXTERNAL_KNOWLEDGE_REQUIRED:
Hace falta referencia externa específica.

INSUFFICIENT_KNOWLEDGE:
No hay conocimiento interno ni fuente externa confiable disponible.
```

---

# 7. Compuerta de suficiencia de conocimiento

Nombre técnico:

```text
KnowledgeSufficiencyGate
```

Nombre en castellano:

```text
Compuerta de Suficiencia de Conocimiento
```

Función:

```text
Antes de investigar, verificar si el sistema tiene conocimiento suficiente del dominio.
```

Ubicación:

```text
OperationalCase Draft
→ Evidence Sufficiency
→ Knowledge Sufficiency
→ External Knowledge Intake si hace falta
→ OperationalCase final
```

---

## Regla vertebral

```text
Cada caso necesita dos suficiencias:
evidencia suficiente del cliente
y conocimiento suficiente del dominio.
```

Si falta evidencia:

```text
se pregunta al dueño.
```

Si falta conocimiento:

```text
se consulta fuente validada.
```

Si falta fuente confiable:

```text
se bloquea o se marca INSUFFICIENT_KNOWLEDGE.
```

---

# 8. Nuevo componente: Source Discovery & Qualification

Nombre técnico:

```text
SourceDiscoveryAndQualification
```

Nombre en castellano:

```text
Descubrimiento y Calificación de Fuentes
```

Función:

```text
Cuando se crea un tanque nuevo, descubrir y calificar fuentes externas idóneas para ese dominio.
```

---

## Pipeline

```text
nuevo_tanque
→ descripción del dominio
→ deep search de fuentes
→ clasificación de instituciones
→ evaluación de confianza
→ detección de temas cubiertos
→ detección de acceso API/SDK/MCP/Web
→ creación de SourceProfiles
→ whitelist pasiva del tanque
```

---

## Resultado

```text
KnowledgeSourceProfile
```

---

# 9. Contrato conceptual de KnowledgeSourceProfile

```python
KnowledgeSourceProfile:
    source_id: str
    tank_id: str
    name: str
    description: str
    institution_type: "OFFICIAL" | "UNIVERSITY" | "TECHNICAL_INSTITUTE" | "INDUSTRY_CHAMBER" | "ACADEMIC_REPOSITORY" | "REGULATORY_BODY" | "PRIVATE_DATABASE" | "OTHER"
    domain_tags: list[str]
    topics_covered: list[str]
    trust_level: "HIGH" | "MEDIUM" | "LOW"
    connection_type: "API" | "SDK" | "MCP" | "WEB" | "DOCUMENT_REPOSITORY" | "DATABASE" | "MANUAL"
    access_mode: "PUBLIC" | "AUTH_REQUIRED" | "PAID" | "PRIVATE" | "UNKNOWN"
    status: "PASSIVE_READY" | "ACTIVE_QUERY" | "DISABLED" | "NEEDS_REVIEW"
    citation_required: bool
    review_required: bool
    license_notes: str
    last_checked_at: str
```

---

# 10. Ejemplo: tanque agro

## Tanque

```text
tanque_agro
```

## Fuentes idóneas posibles

```text
INTA
FAO
universidades agrarias
ministerios agropecuarios
cámaras del agro
servicios meteorológicos
bibliotecas de suelos
documentación técnica sobre riego
documentación técnica sobre fertilización
normativa fitosanitaria
```

## Temas cubiertos

```text
costo por hectárea
margen bruto agropecuario
rinde
fertilizantes
semillas
salinidad
humedad del suelo
riego
combustible
maquinaria
flete
campaña
arrendamiento
clima
plagas
```

## Modo pasivo

El tanque no descarga todo.

Guarda perfiles:

```text
source_id: inta_agro
trust_level: HIGH
topics_covered: costo_hectarea, rinde, fertilizacion, humedad_suelo
status: PASSIVE_READY
```

## Modo activo

Caso complejo:

```text
“Necesito saber si la salinidad y la humedad del suelo me están afectando el rendimiento.”
```

Activación:

```text
KnowledgeGapDetector detecta que falta protocolo técnico.
SourceSelector elige fuentes agro calificadas.
ExternalKnowledgeIntakeEngine recupera referencias.
AntiGarbageFilter descarta ruido.
Curator arma ReferenceBundle.
El caso usa referencia externa + evidencia del productor.
```

---

# 11. Ejemplo: tanque metalúrgica

## Tanque

```text
tanque_metalurgica
```

## Fuentes idóneas posibles

```text
INTI
normas IRAM
universidades técnicas
manuales de manufactura
cámaras industriales
documentación de seguridad
manuales de mantenimiento
```

## Temas cubiertos

```text
BOM
costo por orden
tiempos máquina
merma
mantenimiento
cuello de botella
calidad
seguridad industrial
costos indirectos
mano de obra
```

## Caso complejo

```text
“No sé si estoy presupuestando bien una pieza que pasa por tres máquinas.”
```

Posible brecha:

```text
falta conocimiento sobre imputación de horas máquina y costos indirectos.
```

Uso:

```text
consultar fuente técnica calificada
extraer protocolo o buenas prácticas
aplicarlo solo si el cliente aporta BOM, tiempos, costos y evidencia de producción
```

---

# 12. Ejemplo: tanque gastronomía

## Fuentes idóneas posibles

```text
manuales de food cost
bromatología
cámaras gastronómicas
escuelas de cocina
bibliografía de ingeniería de menú
normativas sanitarias
```

## Temas cubiertos

```text
food cost
merma
receta estándar
costeo por plato
rotación de insumos
menú engineering
bromatología
compras
stock cocina
```

## Caso complejo

```text
“Vendo mucho un plato pero no sé si me deja ganancia.”
```

Probablemente no requiere búsqueda externa profunda si el tanque interno ya sabe food cost.

Puede requerir evidencia del cliente:

```text
receta
ingredientes
costos
precio de venta
ventas por plato
merma
```

Decisión del KnowledgeGapDetector:

```text
EVIDENCE_REQUIRED
```

No:

```text
EXTERNAL_KNOWLEDGE_REQUIRED
```

---

# 13. Filtro anti-basura

Nombre técnico:

```text
AntiGarbageKnowledgeFilter
```

Nombre en castellano:

```text
Filtro Anti-Basura de Conocimiento
```

Función:

```text
Evitar que conocimiento externo irrelevante, débil, viejo, comercial o contaminado entre al caso o al tanque.
```

---

## Debe rechazar

```text
fuente no identificada
contenido sin autor
información vieja sin vigencia
contenido comercial disfrazado de técnico
texto genérico no aplicable al caso
información no aplicable a PyMEs
material sin cita
material sin fecha
contradicción no resuelta
contenido que no aporta a la hipótesis
contenido que no ayuda a variables/evidencia/fórmula/protocolo
contenido demasiado académico sin aplicación operativa
```

---

## Preguntas del filtro

```text
¿Esto responde a la brecha detectada?
¿Esto pertenece al dominio del tanque?
¿La fuente es idónea?
¿Tiene fecha o versión?
¿Es aplicable al tipo de cliente?
¿Sirve para formular hipótesis, variables, evidencia, fórmula o protocolo?
¿Debe usarse solo como referencia o puede promoverse al tanque?
```

---

# 14. SourceSelector

Nombre técnico:

```text
SourceSelector
```

Función:

```text
Elegir qué fuentes calificadas consultar según la brecha del caso.
```

---

## Contrato conceptual

```python
SourceSelection:
    selection_id: str
    case_id: str
    tank_id: str
    knowledge_gap: str
    selected_sources: list[str]
    excluded_sources: list[str]
    selection_reason: str
    min_trust_level: str
```

---

## Ejemplo

Brecha:

```text
protocolo de salinidad de suelo
```

Fuentes seleccionadas:

```text
INTA
universidad agraria
manual técnico de suelos
```

Fuentes excluidas:

```text
blog comercial de fertilizantes
foro sin autor
nota periodística genérica
```

---

# 15. ReferenceBundle

Cuando el motor externo trae conocimiento útil para un caso, no debería meterlo suelto.

Debe empaquetarlo como:

```text
ReferenceBundle
```

---

## Contrato conceptual

```python
ReferenceBundle:
    reference_bundle_id: str
    case_id: str
    tank_id: str
    knowledge_gap: str
    references: list[NormalizedKnowledgeItem]
    extracted_principles: list[str]
    formulas_or_protocols: list[str]
    applicable_variables: list[str]
    warnings: list[str]
    source_refs: list[str]
    generated_at: str
```

---

## Uso

El `ReferenceBundle` ayuda a:

```text
formular mejor la hipótesis;
deducir variables necesarias;
seleccionar fórmulas o protocolos;
comparar contra evidencia del cliente;
redactar limitaciones del reporte.
```

Pero no prueba el caso por sí mismo.

---

# 16. Reglas de uso en DiagnosticReport

El `DiagnosticReport` debe separar:

```text
evidence_used
```

de:

```text
references_used
```

## evidence_used

Evidencia concreta del cliente:

```text
Excel
facturas
extractos
inventario
BOM
recetas
mediciones
fotos
documentos internos
```

## references_used

Fuentes externas:

```text
manual técnico
norma
paper
guía institucional
benchmark
protocolo
```

---

## Regla

```text
evidence_used prueba.
references_used orienta o contextualiza.
```

---

# 17. Estados del tanque específico

Un tanque específico puede pasar por estados:

```text
DRAFT:
estructura inicial.

SOURCE_DISCOVERY:
buscando fuentes idóneas.

SOURCE_QUALIFIED:
fuentes clasificadas.

PASSIVE_READY:
tanque listo con fuentes en reposo.

ACTIVE_ENRICHMENT:
consultando fuentes por un caso.

CURATED_UPDATE_PENDING:
hay candidatos para revisar.

VERSIONED:
nueva versión publicada.

DEPRECATED:
tanque obsoleto o reemplazado.
```

---

# 18. Ciclo de vida completo de un tanque específico

```text
1. Crear definición mínima del tanque.
2. Declarar dominio y subdominios.
3. Ejecutar Source Discovery.
4. Calificar fuentes.
5. Crear whitelist pasiva.
6. Registrar SourceProfiles.
7. Publicar tanque en PASSIVE_READY.
8. Usar tanque en casos normales.
9. Si aparece brecha, activar búsqueda externa.
10. Filtrar y curar.
11. Usar referencia en caso.
12. Si el conocimiento es recurrente, promoverlo.
13. Versionar tanque.
```

---

# 19. Relación con plugins

Cada fuente externa se conecta por plugin.

Tipos:

```text
API
SDK
MCP Server
Web controlado
Document repository
Database
Manual upload
```

---

## Plugin mínimo

```python
KnowledgeSourcePlugin:
    source_id: str
    name: str
    tank_id: str
    connection_type: str
    trust_level: str

    search(query) -> RawKnowledgeBatch
    fetch(item_id) -> RawKnowledgeItem
    normalize(raw) -> NormalizedKnowledgeItem
```

---

## Regla

```text
El plugin no decide.
El plugin trae y normaliza.
```

---

# 20. Relación con MCP Server

MCP permite enchufar fuentes sin meterlas dentro del core.

Arquitectura:

```text
SmartPyme
→ MCP Knowledge Server
→ fuente externa
→ resultado normalizado
→ External Knowledge Intake Engine
→ AntiGarbageFilter
→ Curator
→ ReferenceBundle / KnowledgeCandidate
```

---

## MCP puede exponer

```text
search_sources
search_knowledge
fetch_document
get_metadata
normalize_result
list_available_topics
```

---

## MCP no debe hacer

```text
diagnosticar
modificar el tanque
confirmar hallazgos
ejecutar acciones de negocio
saltarse curación
```

---

# 21. Relación con KnowledgeCandidate y promoción

Si una referencia externa resulta útil de forma recurrente, puede convertirse en candidato de promoción.

```text
ReferenceBundle usado en caso
→ KnowledgeCandidate
→ Curator
→ KnowledgePromotionRecord
→ nueva versión del tanque
```

---

## No todo lo consultado se promueve

Mucho conocimiento externo será de uso puntual.

Solo se promueve si:

```text
es confiable
es recurrente
mejora preguntas
mejora hipótesis
mejora variables
mejora fórmulas/protocolos
mejora buenas prácticas
no contamina el tanque
```

---

# 22. Relación con casos complejos

Los casos simples no deben activar búsqueda externa.

Ejemplo:

```text
pérdida de margen simple en comercio
```

Probablemente alcanza con:

```text
ventas
costos
facturas
lista de precios
tanque_pyme_general
tanque_finanzas
+ contabilidad
+ PyME general
```

Caso complejo:

```text
humedad de suelo + salinidad + rinde + costo por hectárea
```

Probablemente requiere:

```text
tanque_agro
fuentes agro calificadas
ReferenceBundle técnico
```

---

# 23. Política de activación

El motor externo se activa si:

```text
1. el KnowledgeGapDetector detecta brecha de conocimiento;
2. existe fuente calificada;
3. la fuente supera trust_level mínimo;
4. la consulta tiene propósito claro;
5. el conocimiento buscado sirve al caso;
6. no se está reemplazando evidencia del cliente.
```

---

## No se activa si

```text
falta evidencia del cliente;
el caso es simple;
la pregunta es genérica;
no hay fuente confiable;
el resultado no cambiaría la investigación;
el tanque interno ya alcanza.
```

---

# 24. Relación con mayéutica

El conocimiento externo también mejora las preguntas al dueño.

Ejemplo agro:

```text
Para analizar salinidad y humedad necesito:
- ubicación/lote;
- cultivo;
- análisis de suelo si tenés;
- fechas de riego o lluvia;
- rendimiento esperado y real;
- costos de insumos.
```

La fuente externa ayuda a saber qué preguntar.

Pero la información la aporta el productor.

---

# 25. Relación con método hipotético-deductivo

El conocimiento externo ayuda a formular hipótesis mejores.

Ejemplo:

```text
Investigar si existe caída de rendimiento asociada a salinidad o humedad insuficiente del suelo durante la campaña X.
```

Deduce variables:

```text
humedad
salinidad
cultivo
lote
rinde esperado
rinde real
riego
lluvia
fertilización
costo por hectárea
```

Luego exige evidencia.

---

# 26. Relación con tanques generales y específicos

Arquitectura final:

```text
Core operativo
→ tanques transversales
→ tanque PyME general
→ tanque específico sectorial
→ fuente externa calificada
→ evidencia real del cliente
```

Ejemplo:

```text
PyME agro =
core
+ contabilidad
+ finanzas
+ compras
+ proveedores
+ PyME general
+ agro
+ fuentes agro calificadas
+ evidencia del productor
```

---

# 27. Frases rectoras

```text
Cada tanque debe nacer con un mapa de fuentes,
no con una enciclopedia completa.
```

```text
El tanque no sabe todo.
Sabe qué sabe, qué le falta y dónde buscar.
```

```text
Fuente validada en reposo.
Conocimiento específico bajo demanda.
Promoción solo por curación.
```

```text
Brecha de evidencia: vuelve al dueño.
Brecha de conocimiento: consulta fuente idónea.
```

```text
La referencia externa orienta.
La evidencia del cliente prueba.
```

```text
El plugin trae.
El filtro limpia.
El curador decide.
El tanque versionado incorpora.
```

---

# 28. Riesgos

## 28.1 Activar búsqueda externa innecesaria

Riesgo:

```text
el sistema investiga afuera cuando solo falta un Excel del cliente.
```

Mitigación:

```text
distinguir evidence_gap de knowledge_gap.
```

---

## 28.2 Fuente idónea mal elegida

Riesgo:

```text
consultar blogs, notas comerciales o fuentes débiles.
```

Mitigación:

```text
Source Discovery con trust_level y whitelist.
```

---

## 28.3 Contaminación del tanque

Riesgo:

```text
incorporar conocimiento incorrecto o demasiado genérico.
```

Mitigación:

```text
AntiGarbageFilter + Curator + PromotionRecord + versionado.
```

---

## 28.4 Sobrecargar el MVP

Riesgo:

```text
intentar construir este motor antes de tener SmartPyme V1 funcionando.
```

Mitigación:

```text
documentar ahora;
implementar después de TS_026C y DiagnosticReport V1.
```

---

# 29. Implementación futura sugerida

No implementar todavía completo.

Cuando corresponda, dividir en tareas:

```text
TS_028_EXTERNAL_KNOWLEDGE_INTAKE_CONTRACTS
TS_029_SOURCE_DISCOVERY_AND_QUALIFICATION
TS_030_KNOWLEDGE_GAP_DETECTOR
TS_031_KNOWLEDGE_SOURCE_REGISTRY
TS_032_EXTERNAL_KNOWLEDGE_INTAKE_ENGINE_MOCK
TS_033_REFERENCE_BUNDLE_AND_KNOWLEDGE_PROMOTION
```

---

## Archivos posibles

```text
app/contracts/external_knowledge_contract.py
app/contracts/knowledge_gap_contract.py
app/knowledge/source_registry.py
app/knowledge/gap_detector.py
app/knowledge/intake_engine.py
app/knowledge/anti_garbage_filter.py
app/knowledge/curator.py
tests/contracts/test_external_knowledge_contract.py
tests/knowledge/test_gap_detector.py
tests/knowledge/test_source_registry.py
```

---

# 30. Orden recomendado

Aunque este diseño es estratégico, el orden inmediato sigue siendo:

```text
1. Resolver provider Gemini/Vertex/ADC en Hermes.
2. Sincronizar documentos pendientes.
3. Implementar TS_026C_SYMPTOM_PATHOLOGY_CATALOG.
4. Construir DiagnosticReport V1.
5. Recién después implementar motor externo mínimo.
```

---

# 31. Cierre

Este diseño permite que SmartPyme escale sin pretender saber todo desde el inicio.

El sistema final no será una base cerrada.

Será una arquitectura que puede:

```text
crear tanques mínimos;
descubrir fuentes idóneas;
dejarlas conectadas en reposo;
detectar brechas de conocimiento;
activar investigación externa bajo demanda;
filtrar basura;
usar referencias sin confundirlas con evidencia;
promover conocimiento validado;
versionar tanques;
mejorar con casos reales.
```

Eso convierte los tanques en organismos vivos, pero protegidos.

No se trata de succionar todo.

Se trata de succionar lo necesario, desde donde corresponde, con trazabilidad y control.
