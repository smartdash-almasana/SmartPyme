# SmartPyme — Motor de Abastecimiento Externo de Conocimiento

## Estado

Documento conceptual crítico de arquitectura.

Este documento desarrolla la idea de que los **tanques de conocimiento** de SmartPyme no deben depender solamente de conocimiento cargado manualmente o definido internamente, sino que deben poder abastecerse de fuentes externas especializadas mediante una arquitectura enchufable, auditable y versionada.

La metáfora original es clara:

```text
una bomba de succión de conocimiento
una aspiradora de conocimiento externo
un motor enchufable de investigación profunda
```

Traducción técnica recomendada:

```text
External Knowledge Intake Engine
```

Nombre en castellano operativo:

```text
Motor de Abastecimiento Externo de Conocimiento
```

Nombre alternativo:

```text
Capa de Ingesta de Conocimiento Externo
```

---

## Tesis central

Los tanques de conocimiento no deben ser enciclopedias cerradas.

Deben ser depósitos vivos, alimentados por:

```text
- conocimiento interno;
- experiencia documentada;
- casos reales validados;
- fuentes externas autorizadas;
- APIs;
- SDKs;
- MCP Servers;
- bibliotecas públicas;
- organismos técnicos;
- universidades;
- papers;
- normas;
- manuales;
- bases sectoriales.
```

Pero con una regla estricta:

```text
El conocimiento externo no entra directo al tanque.
Primero se busca, se extrae, se normaliza, se valida, se cita y se versiona.
```

---

# 1. Problema que resuelve

Los tanques de conocimiento de SmartPyme pueden empezar mínimos.

Ejemplo:

```text
tanque_pyme_general
tanque_finanzas
tanque_compras
tanque_proveedores
tanque_agro
tanque_metalurgica
tanque_gastronomia
tanque_salud
```

Pero para ser realmente útiles, algunos rubros necesitan conocimiento especializado.

Ejemplos:

```text
agro:
- costos por hectárea;
- fertilizantes;
- rindes;
- campañas;
- maquinaria;
- logística rural;
- información climática;
- prácticas del INTA.

industria:
- normas técnicas;
- eficiencia productiva;
- mantenimiento;
- BOM;
- calidad;
- seguridad;
- referencias del INTI.

salud:
- protocolos;
- turnos;
- facturación médica;
- indicadores asistenciales;
- cumplimiento documental.

gastronomía:
- food cost;
- merma;
- ingeniería de menú;
- bromatología;
- compras de insumos.

construcción:
- materiales; 
- cómputo y presupuesto;
- certificaciones;
- avance de obra;
- mano de obra;
- normas técnicas.
```

No conviene cargar todo eso manualmente desde el día uno.

La arquitectura debe permitir que SmartPyme consulte, absorba y organice conocimiento externo cuando lo necesita.

---

# 2. Idea central

La arquitectura correcta es:

```text
Tanque interno mínimo
+ conectores externos
+ motor de investigación
+ curación
+ versionado
= tanque enriquecido y auditado
```

Otra formulación:

```text
El core opera.
El tanque orienta.
El motor externo investiga.
La curación valida.
El versionado incorpora.
```

---

# 3. Relación con la arquitectura de tanques

Los tanques actuales contienen o pueden contener:

```text
- síntomas;
- patologías;
- fórmulas;
- protocolos;
- variables;
- evidencias;
- benchmarks;
- buenas prácticas;
- preguntas mayéuticas;
- lenguaje del rubro;
- riesgos típicos;
- modelos operativos;
- criterios de diagnóstico;
- criterios de impacto;
- skills especializadas.
```

El Motor de Abastecimiento Externo de Conocimiento agrega una capa nueva:

```text
fuentes externas autorizadas
```

Es decir, el tanque no solo almacena conocimiento. También puede declarar de dónde obtener conocimiento cuando necesita ampliar, verificar o actualizar su base.

---

# 4. Principio rector

```text
Los tanques no tienen que saber todo.
Tienen que saber qué saben, qué les falta y dónde buscar con seguridad.
```

Esto es fundamental.

Un tanque mínimo puede contener:

```text
- estructura semántica;
- síntomas iniciales;
- patologías principales;
- preguntas de arranque;
- fuentes externas confiables;
- reglas de curación.
```

Y usar el motor externo para ampliar:

```text
- referencias;
- benchmarks;
- normas;
- indicadores;
- prácticas actualizadas;
- material técnico.
```

---

# 5. Arquitectura general

```text
Knowledge Tank
│
├── Núcleo interno
│   ├── síntomas
│   ├── patologías
│   ├── fórmulas
│   ├── protocolos
│   ├── variables
│   ├── evidencia requerida
│   ├── buenas prácticas
│   └── preguntas mayéuticas
│
├── Fuentes externas autorizadas
│   ├── APIs
│   ├── SDKs
│   ├── MCP Servers
│   ├── documentos públicos
│   ├── repositorios privados
│   ├── bases académicas
│   ├── organismos técnicos
│   └── bibliotecas sectoriales
│
├── Motor de abastecimiento externo
│   ├── busca
│   ├── recupera
│   ├── descarga
│   ├── normaliza
│   ├── resume
│   ├── clasifica
│   ├── extrae conceptos
│   ├── compara fuentes
│   └── propone incorporación
│
└── Curación y versionado
    ├── valida fuente
    ├── etiqueta dominio
    ├── registra evidencia
    ├── cita origen
    ├── calcula confianza
    ├── evita contaminación
    ├── genera propuesta
    └── publica versión del tanque
```

---

# 6. Componentes principales

## 6.1 Knowledge Tank

El tanque contiene conocimiento operativo del dominio.

Ejemplo:

```text
tanque_agro
tanque_metalurgica
tanque_gastronomia
tanque_contabilidad
tanque_finanzas
```

El tanque debe poder declarar:

```text
tank_id
domain_tags
symptoms
pathologies
evidence_types
skills
formulas_or_protocols
trusted_sources
source_plugins
curation_rules
version
```

---

## 6.2 Knowledge Source Plugin

Un plugin representa una fuente externa enchufable.

Ejemplos:

```text
plugin_inta_agro
plugin_inti_industria
plugin_normativa_laboral
plugin_afip_impuestos
plugin_universidad_costos
plugin_benchmark_gastronomia
plugin_weather_agro
plugin_public_prices
plugin_supplier_catalogs
```

El plugin no debe decidir.  
El plugin solo recupera y normaliza conocimiento candidato.

---

## 6.3 Knowledge Intake Engine

El motor coordina la búsqueda, descarga, extracción y clasificación.

No incorpora automáticamente al tanque.

Produce:

```text
KnowledgeCandidate
```

o lotes de:

```text
KnowledgeCandidateBatch
```

---

## 6.4 Knowledge Curator

El curador valida si el material externo sirve.

Puede ser:

```text
- determinístico;
- asistido por IA;
- humano;
- mixto.
```

Evalúa:

```text
- confiabilidad de fuente;
- actualidad;
- relevancia;
- dominio;
- duplicados;
- contradicciones;
- aplicabilidad a PyME;
- riesgo de mala interpretación;
- licencia o permiso de uso;
- calidad documental.
```

---

## 6.5 Knowledge Promotion

Cuando el material es validado, se promueve.

Estados posibles:

```text
RAW
NORMALIZED
CANDIDATE
CURATED
APPROVED
PROMOTED
REJECTED
DEPRECATED
```

Solo `PROMOTED` entra al tanque productivo.

---

# 7. Contrato conceptual de KnowledgeSourcePlugin

```python
KnowledgeSourcePlugin:
    source_id: str
    name: str
    description: str
    domain_tags: list[str]
    connection_type: "API" | "SDK" | "MCP" | "WEB" | "DOCUMENT_REPOSITORY" | "DATABASE"
    auth_required: bool
    trust_level: "HIGH" | "MEDIUM" | "LOW"
    allowed_queries: list[str]
    rate_limits: dict
    license_notes: str

    fetch(query) -> RawKnowledgeBatch
    normalize(raw) -> NormalizedKnowledgeItems
```

---

## Campos recomendados

```text
source_id:
identificador único del plugin.

name:
nombre legible.

domain_tags:
rubros o temas donde aplica.

connection_type:
forma de conexión.

auth_required:
si requiere credenciales.

trust_level:
nivel inicial de confianza de la fuente.

allowed_queries:
tipos de consultas permitidas.

rate_limits:
restricciones de uso.

license_notes:
restricciones legales o de licencia.

fetch:
método de recuperación.

normalize:
método de normalización al formato interno.
```

---

# 8. Contrato conceptual de RawKnowledgeBatch

```python
RawKnowledgeBatch:
    batch_id: str
    source_id: str
    query: str
    fetched_at: str
    raw_items: list[dict]
    metadata: dict
```

Representa lo que llegó desde la fuente sin curación.

---

# 9. Contrato conceptual de NormalizedKnowledgeItem

```python
NormalizedKnowledgeItem:
    item_id: str
    source_id: str
    title: str
    content_summary: str
    content_type: str
    domain_tags: list[str]
    url: str | None
    document_id: str | None
    fetched_at: str
    published_at: str | None
    authors: list[str]
    raw_ref: str
    metadata: dict
```

Este objeto ya tiene forma interna, pero todavía no significa que sea verdadero o incorporable.

---

# 10. Contrato conceptual de KnowledgeCandidate

```python
KnowledgeCandidate:
    candidate_id: str
    source_id: str
    tank_id: str
    candidate_type: "SYMPTOM" | "PATHOLOGY" | "FORMULA" | "PROTOCOL" | "BENCHMARK" | "GOOD_PRACTICE" | "EVIDENCE_REQUIREMENT" | "MAYEUTIC_QUESTION" | "RISK" | "IMPACT_METRIC"
    title: str
    extracted_content: dict
    source_refs: list[str]
    confidence_score: float
    curation_status: "CANDIDATE" | "APPROVED" | "REJECTED" | "NEEDS_REVIEW"
    notes: str
```

---

# 11. Contrato conceptual de KnowledgePromotionRecord

```python
KnowledgePromotionRecord:
    promotion_id: str
    candidate_id: str
    tank_id: str
    promoted_by: str
    promoted_at: str
    previous_tank_version: str
    new_tank_version: str
    rationale: str
    source_refs: list[str]
```

Este registro prueba que una pieza de conocimiento externo pasó al tanque de forma controlada.

---

# 12. Pipeline completo

```text
1. El tanque detecta necesidad de conocimiento.
2. Se selecciona una fuente externa autorizada.
3. El plugin consulta la fuente.
4. El motor recupera material.
5. Se normaliza el contenido.
6. Se extraen conceptos candidatos.
7. Se clasifica por tipo y dominio.
8. Se evalúa fuente, relevancia y actualidad.
9. Se genera KnowledgeCandidate.
10. El curador aprueba, rechaza o pide revisión.
11. Si se aprueba, se genera KnowledgePromotionRecord.
12. El tanque publica una nueva versión.
```

---

# 13. Ejemplo: agro e INTA

## Situación

Cliente agro pregunta:

```text
“¿Estoy calculando mal el costo por hectárea?”
```

## Tanques activos

```text
tanque_pyme_general
tanque_finanzas
tanque_costos
tanque_agro
```

## Fuente externa posible

```text
plugin_inta_agro
```

## El tanque agro sabe que debe buscar

```text
- costo por hectárea;
- rinde;
- campaña;
- fertilizante;
- semillas;
- combustible;
- maquinaria;
- fletes;
- arrendamiento;
- labores;
- margen bruto agropecuario.
```

## Pipeline

```text
demanda del cliente
→ síntoma: incertidumbre_costo_hectarea
→ hipótesis: investigar si el costo por hectárea está subestimado
→ tanque_agro consulta fuentes externas
→ plugin_inta_agro recupera material técnico
→ se extraen variables típicas
→ se validan contra evidencia del cliente
→ se genera OperationalCase
→ se ejecuta investigación
→ se produce DiagnosticReport
```

## Resultado posible

SmartPyme no dice:

```text
“INTA dice X, entonces usted está mal.”
```

Dice:

```text
“Según la evidencia aportada por el cliente y las referencias técnicas consultadas,
faltan imputaciones de combustible, labores y flete para estimar correctamente el costo por hectárea.
Con la información actual, el diagnóstico es INSUFFICIENT_EVIDENCE o CONFIRMED según datos disponibles.”
```

---

# 14. Ejemplo: industria e INTI

## Situación

Cliente industrial dice:

```text
“No sé si el costo de producción está bien calculado.”
```

## Tanques activos

```text
tanque_pyme_general
tanque_costos
tanque_produccion_industrial
tanque_metalurgica
```

## Fuente externa posible

```text
plugin_inti_industria
plugin_normas_tecnicas
plugin_universidad_costos_industriales
```

## Conceptos buscados

```text
- BOM;
- costos indirectos;
- tiempos máquina;
- merma;
- mantenimiento;
- eficiencia productiva;
- costo de mano de obra;
- costos por orden de producción.
```

## Uso correcto

La fuente externa aporta modelos, protocolos o benchmarks.

El diagnóstico se hace con evidencia del cliente.

```text
fuente externa = referencia
evidencia del cliente = prueba del caso
```

---

# 15. Ejemplo: normativa laboral / liquidación de sueldos

## Situación

Microservicio:

```text
“Liquidame estos sueldos.”
```

## Fuentes posibles

```text
plugin_normativa_laboral
plugin_convenios_colectivos
plugin_afip
plugin_escalas_salariales
```

## Riesgo

Este dominio puede ser legalmente sensible.

El sistema debe ser prudente:

```text
- citar fuente;
- indicar fecha de actualización;
- permitir revisión por contador;
- evitar prometer exactitud legal absoluta;
- registrar versión normativa usada.
```

---

# 16. Tres niveles de conocimiento

## Nivel 1 — Tanque base interno

Conocimiento estable, probado y versionado.

Ejemplo: 

```text
sospecha_perdida_margen
desalineacion_costo_precio
ventas_pos
facturas_proveedor
skill_margin_leak_audit
```

---

## Nivel 2 — Fuente externa consultable

Material externo usado en tiempo de investigación.

Ejemplo:

```text
manual técnico,
norma,
paper,
API pública,
base estadística,
reporte de organismo.
```

Puede usarse como referencia, pero no queda automáticamente incorporado.

---

## Nivel 3 — Conocimiento promovido

Material validado que pasa a formar parte del tanque.

Ejemplo:

```text
nuevo benchmark,
nueva buena práctica,
nueva variable requerida,
nuevo protocolo,
nuevo tipo de evidencia.
```

---

# 17. Regla de oro

```text
MCP trae.
El motor normaliza.
La curación decide.
El tanque versionado incorpora.
```

---

# 18. Relación con MCP Servers

MCP encaja muy bien como protocolo de conexión.

Arquitectura:

```text
SmartPyme / Hermes
→ MCP Knowledge Server
→ fuente externa
→ respuesta normalizada
→ Knowledge Intake Layer
→ KnowledgeCandidate
→ Curator
→ Tank Version
```

---

## Qué puede hacer un MCP Knowledge Server

```text
buscar documentos;
consultar APIs;
leer bases;
extraer metadatos;
descargar archivos;
devolver resultados normalizados;
consultar catálogos externos;
validar disponibilidad de fuente.
```

---

## Qué NO debe hacer

Un MCP Knowledge Server no debe:

```text
modificar el tanque directamente;
confirmar diagnóstico;
crear hallazgos definitivos;
ejecutar acciones de negocio;
saltarse curación;
escribir en core sin autorización.
```

---

# 19. Relación con Deep Research

El sistema puede tener una capacidad de investigación profunda.

Pero debe estar gobernada.

Deep Research puede:

```text
- buscar múltiples fuentes;
- comparar versiones;
- resumir materiales largos;
- extraer conceptos;
- detectar contradicciones;
- generar candidatos;
- citar fuentes;
- proponer incorporación.
```

No debe:

```text
- incorporar sin revisión;
- diagnosticar sin evidencia del cliente;
- sustituir al motor determinístico;
- mezclar referencias externas con hechos del caso.
```

---

# 20. Separación crítica: referencia externa vs evidencia del caso

Esta distinción es fundamental.

## Referencia externa

Es conocimiento general.

Ejemplos:

```text
manual del INTA;
norma técnica;
paper académico;
benchmark sectorial;
guía de buenas prácticas.
```

Responde:

```text
¿Cómo suele analizarse este problema?
¿Qué variables importan?
Qué rango es razonable?
Qué protocolo aplica?
```

## Evidencia del caso

Es información concreta del cliente.

Ejemplos:

```text
Excel de ventas;
facturas propias;
extracto bancario;
inventario;
recetas;
órdenes de producción;
fotos;
documentos internos.
```

Responde:

```text
¿Qué ocurrió en este negocio?
```

---

## Regla

```text
La referencia externa orienta.
La evidencia del caso prueba.
```

Sin evidencia del cliente, no hay diagnóstico confirmado.

---

# 21. Ranking de confianza de fuentes

Las fuentes deben tener niveles de confianza.

Ejemplo:

```text
TRUST_HIGH:
organismos oficiales, universidades, normas, documentación técnica primaria.

TRUST_MEDIUM:
consultoras reconocidas, cámaras sectoriales, papers secundarios, manuales técnicos.

TRUST_LOW:
blogs, foros, notas comerciales, contenido sin autor claro.
```

---

## Campos sugeridos

```text
trust_level
source_type
source_owner
last_updated
citation_required
review_required
license_status
```

---

# 22. Control de contaminación del tanque

Riesgo principal:

```text
la aspiradora chupa basura.
```

Mitigaciones:

```text
- fuentes permitidas;
- listas blancas por dominio;
- citas obligatorias;
- fecha de consulta;
- hash o document_id;
- clasificación por confianza;
- validación humana o automática;
- tests de regresión del tanque;
- versionado;
- no incorporación directa;
- posibilidad de deprecar conocimiento viejo.
```

---

# 23. Versionado del tanque

Cada tanque debe tener versiones.

Ejemplo:

```text
tanque_agro@0.1.0
tanque_agro@0.2.0
tanque_agro@0.3.0
```

Cada promoción de conocimiento debe indicar:

```text
qué cambió;
por qué cambió;
de dónde salió;
quién lo aprobó;
qué fuente lo respalda;
qué versión reemplaza.
```

---

# 24. Estados del conocimiento externo

```text
RAW:
material recién traído.

NORMALIZED:
convertido a estructura interna.

CANDIDATE:
concepto extraído y candidato.

NEEDS_REVIEW:
requiere revisión.

APPROVED:
aprobado por curación.

PROMOTED:
incorporado al tanque.

REJECTED:
descartado.

DEPRECATED:
antes válido, ahora obsoleto.
```

---

# 25. Relación con los tanques vivos

Los tanques se enriquecen por dos vías:

```text
1. casos reales validados;
2. fuentes externas curadas.
```

Esto produce un ciclo:

```text
tanque mínimo
→ caso real
→ nuevo aprendizaje
→ fuente externa
→ validación
→ versión nueva
→ mejores preguntas
→ mejores casos
→ mejores reportes
```

---

# 26. Relación con Asertividades Operativas

El motor externo también puede generar asertividades.

Ejemplo:

```text
El usuario aportó información insuficiente.
SmartPyme consultó referencia externa.
Detectó que faltaba una variable crítica.
El usuario luego subió esa evidencia.
Se habilitó el caso.
```

Asertividad:

```text
CLARIFICATION_RESOLVED
CASE_ENABLED
REFERENCE_APPLIED
```

Pero siempre distinguiendo:

```text
la referencia ayudó a formular;
la evidencia del cliente permitió confirmar.
```

---

# 27. Relación con microservicios

Los microservicios pueden usar conocimiento externo sin abrir un caso completo.

Ejemplo:

```text
liquidación de sueldos
conciliación bancaria
plantilla de costos agro
cálculo de food cost
plantilla de producción
macro sectorial
```

El microservicio puede consultar:

```text
- normativa;
- escalas;
- benchmarks;
- fórmulas;
- plantillas;
- protocolos.
```

Pero debe registrar:

```text
fuente usada;
fecha;
versión;
resultado entregado;
limitaciones.
```

---

# 28. Relación con comercio conversacional

El bot puede usar esta capa para vender mejor.

Ejemplo:

```text
“Para este rubro puedo usar referencias técnicas agropecuarias y pedirte los datos mínimos para estimar costo por hectárea. Si querés, empezamos con una plantilla simple.”
```

O:

```text
“Para revisar producción metalúrgica necesito BOM, horas máquina y costos de insumo. Puedo prepararte una plantilla inicial basada en buenas prácticas del rubro.”
```

Esto convierte conocimiento externo en valor comercial inmediato.

---

# 29. Relación con Palantir Principles

Este motor conecta con la idea de ontología operativa.

El conocimiento externo puede crear o enriquecer:

```text
OperationalObject
OperationalLink
ActionType
ActionRecord
CaseTimeline
```

Ejemplo:

```text
fuente externa define una nueva variable relevante;
esa variable se incorpora al tanque;
luego se usa en un OperationalCase;
el caso genera DiagnosticReport;
el reporte genera ActionRecord;
el impacto entra en timeline.
```

---

# 30. Posible estructura técnica futura

```text
app/knowledge/
  __init__.py
  intake_engine.py
  curator.py
  promotion.py
  source_registry.py

app/knowledge/contracts/
  knowledge_source_plugin.py
  raw_knowledge_batch.py
  normalized_knowledge_item.py
  knowledge_candidate.py
  knowledge_promotion_record.py

app/knowledge/plugins/
  inta_agro.py
  inti_industria.py
  normativa_laboral.py
  afip.py
  university_research.py

app/catalogs/knowledge_tanks/
  base.py
  registry.py
  transversal/
  sectors/
```

---

# 31. Posible estructura por MCP

```text
mcp_servers/
  knowledge_inta_agro_server/
  knowledge_inti_industry_server/
  knowledge_normative_server/
  knowledge_academic_search_server/
```

Cada MCP Server debería exponer herramientas como:

```text
search_knowledge
fetch_document
get_metadata
normalize_result
list_available_sources
```

---

# 32. Interfaz conceptual de búsqueda

```python
ExternalKnowledgeRequest:
    request_id: str
    tank_id: str
    domain_tags: list[str]
    query: str
    purpose: "REFERENCE" | "BENCHMARK" | "PROTOCOL" | "FORMULA" | "GOOD_PRACTICE" | "EVIDENCE_REQUIREMENT"
    max_sources: int
    min_trust_level: str
```

---

## Respuesta conceptual

```python
ExternalKnowledgeResponse:
    request_id: str
    items: list[NormalizedKnowledgeItem]
    candidates: list[KnowledgeCandidate]
    source_summary: str
    warnings: list[str]
```

---

# 33. Política de incorporación

Ningún conocimiento externo debe incorporarse si no cumple:

```text
1. fuente identificada;
2. fecha de consulta;
3. dominio aplicable;
4. tipo de conocimiento claro;
5. relación con síntoma/patología/skill/evidencia;
6. confianza mínima;
7. cita o referencia;
8. no contradicción grave con tanque actual sin revisión;
9. justificación de promoción;
10. versión nueva del tanque.
```

---

# 34. Preguntas que el motor debe responder

Antes de consultar:

```text
¿Qué necesita saber el tanque?
¿Para qué lo necesita?
¿Es referencia, fórmula, protocolo o benchmark?
¿Qué fuente está autorizada?
¿Qué nivel de confianza se exige?
```

Después de consultar:

```text
¿Qué se encontró?
¿De dónde salió?
¿Cuándo se consultó?
¿Es aplicable a este dominio?
¿Es aplicable a PyMEs reales?
¿Qué parte puede convertirse en candidato?
¿Qué parte solo sirve como referencia?
```

Antes de promover:

```text
¿Debe entrar al tanque?
¿Debe entrar como síntoma, patología, protocolo, fórmula o buena práctica?
¿Requiere revisión humana?
¿Qué versión del tanque modifica?
```

---

# 35. Riesgos principales

## 35.1 Alucinación por fuentes externas

Riesgo:

```text
el sistema resume mal o inventa sobre una fuente.
```

Mitigación:

```text
citas, extractos, source_refs, hash documental, validación.
```

---

## 35.2 Fuente de baja calidad

Riesgo:

```text
incorporar conocimiento incorrecto.
```

Mitigación:

```text
trust_level, whitelist, review_required.
```

---

## 35.3 Confusión entre referencia y prueba

Riesgo: 

```text
usar un paper como si probara el caso del cliente.
```

Mitigación:

```text
referencia externa orienta; evidencia del cliente prueba.
```

---

## 35.4 Contaminación del tanque

Riesgo:

```text
el tanque se llena de conceptos inconsistentes.
```

Mitigación:

```text
curación, versionado, tests, deprecación.
```

---

## 35.5 Dependencia excesiva de fuentes externas

Riesgo:

```text
el sistema no funcione si una API cae.
```

Mitigación:

```text
cache, tanque base, fuentes alternativas, modo degradado.
```

---

## 35.6 Problemas legales/licencia

Riesgo:

```text
usar material sin permiso o dar asesoramiento regulatorio erróneo.
```

Mitigación:

```text
license_notes, disclaimers, revisión profesional en dominios sensibles.
```

---

# 36. Implementación mínima recomendada

No construir todo de golpe.

MVP conceptual:

```text
1. KnowledgeSourcePlugin como contrato.
2. SourceRegistry con fuentes mock.
3. KnowledgeCandidate.
4. Curator mínimo determinístico.
5. PromotionRecord.
6. Un plugin simulado: plugin_inta_agro_mock.
7. Tests.
```

Sin llamadas reales a APIs al principio.

---

## V1 técnica sugerida

```text
TS_028_EXTERNAL_KNOWLEDGE_INTAKE_CONTRACTS
```

Archivos posibles:

```text
app/contracts/external_knowledge_contract.py
tests/contracts/test_external_knowledge_contract.py
docs/architecture/EXTERNAL_KNOWLEDGE_INTAKE_ENGINE.md
```

---

## V2 técnica sugerida

```text
TS_029_KNOWLEDGE_SOURCE_REGISTRY
```

Archivos posibles:

```text
app/knowledge/source_registry.py
tests/knowledge/test_source_registry.py
```

---

## V3 técnica sugerida

```text
TS_030_KNOWLEDGE_INTAKE_ENGINE_MOCK
```

Archivos posibles:

```text
app/knowledge/intake_engine.py
tests/knowledge/test_intake_engine.py
```

---

# 37. No desplazar prioridades

Este motor es estratégico, pero no debe desplazar la prioridad inmediata:

```text
1. Resolver provider Gemini/Vertex/ADC en Hermes.
2. Sincronizar documentación pendiente.
3. Implementar TS_026C_SYMPTOM_PATHOLOGY_CATALOG.
4. Luego evaluar capa externa de conocimiento.
```

El motor externo puede documentarse ahora y construirse después.

---

# 38. Frases rectoras

```text
Los tanques no son enciclopedias cerradas.
Son depósitos vivos, abastecidos por fuentes internas y externas, protegidos por curación, evidencia y versionado.
```

```text
El tanque mínimo orienta.
El motor externo investiga.
La curación convierte información en conocimiento operativo.
```

```text
SmartPyme no solo consulta conocimiento.
Construye conocimiento operativo validado a partir de fuentes externas y casos reales.
```

```text
MCP trae.
El motor normaliza.
La curación decide.
El tanque versionado incorpora.
```

```text
La referencia externa orienta.
La evidencia del cliente prueba.
```

---

# 39. Cierre

La idea es precisa y potente.

Permite que SmartPyme escale de un sistema con tanques mínimos a un sistema capaz de conectarse con fuentes técnicas, científicas, regulatorias y sectoriales.

Pero debe hacerlo sin contaminar el core y sin transformar cada consulta externa en verdad automática.

La arquitectura correcta es:

```text
fuente externa
→ plugin
→ motor de abastecimiento
→ normalización
→ candidato
→ curación
→ promoción
→ tanque versionado
→ uso en casos futuros
```

Así SmartPyme puede crecer por rubro sin tener que saberlo todo desde el inicio.

El sistema no necesita ser omnisciente.

Necesita saber:

```text
qué buscar,
dónde buscar,
cómo validar,
cómo citar,
cómo versionar,
cómo aplicar
y cuándo no usar lo encontrado.
```
