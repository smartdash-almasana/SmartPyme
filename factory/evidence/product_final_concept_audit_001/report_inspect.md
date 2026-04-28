# product_final_concept_audit_001

Fecha: 2026-04-28
SHA auditado: `0152f2607d94a998f0c0f31aa2cf9c596b0b0ce9`
Modo: `product_architecture_audit`

## VEREDICTO_EJECUTIVO

VEREDICTO: `NO_VALIDADO` como producto final implementado; `CORRECTO` como maqueta conceptual conectada al repo real.

SmartPyme debe fabricarse como un sistema operativo de interpretacion, calculo y toma de decisiones para PyMEs. Su forma final no es una app generica ni una agencia de tareas manuales: es un kernel gobernado que recibe fuentes reales, las transforma en evidencia, normaliza datos, resuelve entidades, bloquea ante incertidumbre, compara fuentes y convierte diferencias cuantificadas en hallazgos accionables para el owner.

El repo actual ya contiene una base tecnica relevante: bridge MCP, jobs, clarifications, ingestion documental, EvidenceStore, get_evidence, reconciliation parcial, hallazgos parcial y factory Hermes. No evidencia todavia un onboarding conversacional de producto, catalogo runtime de servicios PyME, flujos Excel/macros, stock, impuestos, produccion, suscripciones ni UI owner-ready.

## DEFINICION_PRODUCTO_FINAL

SmartPyme final debe tener tres superficies separadas:

1. Owner cockpit: bot conversacional y panel minimo para que el duenio explique su negocio, suba archivos, vea hallazgos, apruebe acciones y consulte estado.
2. SmartPyme Core: kernel deterministico que persiste jobs, evidencias, clarifications, normalizacion, entity resolution, reconciliacion, hallazgos, comunicacion y acciones.
3. Factory / servicios: capa operativa para fabricar soluciones simples o recurrentes: Excel, macros, limpieza documental, conciliaciones, reportes, automatizaciones y auditorias.

El producto debe entrar por problemas concretos del owner, no por features. Cada problema se traduce a un plan operativo con fuentes requeridas, criterio de aceptacion, riesgo, evidencia y decision de servicio unico o suscripcion.

## QUE_ES_SMARTPYME

- Un sistema operativo PyME para ganar mas dinero, perder menos dinero y ahorrar tiempo.
- Un interprete gobernado entre conversacion humana y kernel tecnico.
- Un motor de evidencia: no responde con hechos de negocio sin fuente recuperable.
- Un sistema fail-closed: si hay ambiguedad critica, crea clarification y bloquea el avance.
- Una fabrica de soluciones graduales: primero solucion simple si alcanza; luego automatizacion o sistema recurrente si el caso lo justifica.
- Un motor de hallazgos: cada hallazgo debe tener entidad, comparacion explicita, diferencia cuantificada y evidencia.

## QUE_NO_ES_SMARTPYME

- No es un chatbot libre que improvisa consejos.
- No es un ERP completo desde el dia uno.
- No es una consultora que vende trabajo manual sin trazabilidad.
- No es un sistema que mezcla productos externos o legados como fuente de verdad.
- No es una app de Excel solamente; Excel es una salida posible cuando es suficiente.
- No es un pipeline infinito de IA: la IA interpreta, el kernel decide.
- No debe prometer stock, impuestos, produccion o automatizaciones como implementadas si no hay contrato, servicio y tests.

## TRES_PILARES_DE_VALOR

### Dinero: ganar mas

- Detectar oportunidades de precio, margen, ventas, stock y proveedores.
- Comparar ventas/costos/compras para sugerir decisiones con impacto economico.
- Transformar documentos y datos dispersos en metricas confiables.

### Dinero: perder menos

- Detectar duplicados, pagos mal imputados, conciliaciones pendientes, diferencias de montos, faltantes y fugas.
- Reconciliar fuentes antes de generar hallazgos.
- Bloquear ante entidades ambiguas, montos dudosos o evidencia insuficiente.

### Tiempo: ahorrar mas

- Resolver rapido con Excel con formulas cuando alcanza.
- Automatizar tareas puntuales con macros o scripts cuando el retorno lo justifica.
- Escalar a ingesta masiva, auditoria documental o sistema recurrente solo cuando el volumen/riesgo lo pide.

## ONBOARDING_CONVERSACIONAL_INCREMENTAL

El onboarding debe ser un bot para el owner PyME, conectado por MCP al core cuando necesite crear jobs, guardar clarifications, ingerir documentos o consultar evidencia.

Flujo recomendado:

1. Identificacion del negocio: rubro, tamanio aproximado, canales de venta, cantidad de empleados, herramientas actuales.
2. Dolor principal: vender mas, perder menos, ahorrar tiempo, ordenar datos, conciliacion, stock, impuestos, produccion, compras, ventas, documentacion u otro.
3. Fuente disponible: Excel, PDFs, tickets, remitos, banco, MercadoLibre, sistema contable, carpetas historicas, emails u otros.
4. Urgencia e impacto: cuanto dinero/tiempo esta en juego, frecuencia del problema, si hay fecha limite.
5. Camino gradual:
   - Nivel 1: solucion unica simple, barata y entregable rapido.
   - Nivel 2: automatizacion puntual con macro/script/reporte.
   - Nivel 3: servicio recurrente con jobs, evidencia, conciliaciones y hallazgos.
   - Nivel 4: sistema completo con integraciones y action engine, solo con contratos cerrados.
6. Plan operativo: objetivo, fuentes requeridas, criterios de aceptacion, bloqueos y tipo de servicio.
7. Confirmacion humana: el owner aprueba alcance, costo y datos a usar.

Regla: el onboarding comercial no define estados tecnicos. Debe traducir la conversacion a contratos del core y crear clarifications cuando falte informacion.

## CATALOGO_DE_SERVICIOS

| Servicio | Tipo | Nivel | Estado repo real |
|---|---:|---:|---|
| Excel con formulas como solucion rapida | unico | 1 | No evidenciado como runtime |
| Excel con macros como automatizacion puntual | unico | 2 | No evidenciado |
| Reparacion y limpieza de archivos Excel | unico | 1-2 | No evidenciado |
| Conversion de PDFs/documentos a Excel | unico | 1-2 | Ingesta PDF parcial; conversion a Excel no evidenciada |
| Lectura masiva de PDFs, tickets, remitos y documentacion historica | unico o suscripcion | 2-3 | Ingesta archivo unico evidenciada; batch pendiente |
| Calculos de produccion, ventas, impuestos, costos y rentabilidad | unico o suscripcion | 2-3 | Calculators y servicios core existen parcialmente; dominios especificos no cerrados |
| Conciliacion bancaria y cruce de fuentes | unico o suscripcion | 3 | Reconciliation parcial; no expuesto por MCP |
| Control de stock y deteccion de perdida de control | suscripcion | 3 | No evidenciado como modulo |
| Hallazgos accionables para decisiones del owner | suscripcion | 3 | Dominio parcial; no gobierna runtime MCP |
| Automatizaciones recurrentes bajo suscripcion | suscripcion | 3-4 | Action engine conceptual/parcial; ejecucion real no cerrada |
| Servicios unicos por demanda | unico | 1-2 | Debe fabricarse sobre jobs y evidencia |

## MODULOS_PRODUCTO

1. Onboarding Owner: conversacion incremental, clasificacion de dolor y plan operativo. Falta implementar.
2. Job / Plan: `create_job`, `get_job_status`, `OperationalPlanContract`. Implementado minimo.
3. Evidence / Ingestion: `ingest_document`, raw registry, chunks, citations y `get_evidence`. Implementado minimo para documento local.
4. Excel Service: formulas, macros, limpieza y exportacion. No evidenciado.
5. Document Service: PDFs/documentos, OCR/parsing, batch, retrieval y conversion. Parcial.
6. Calculation Service: ventas, costos, impuestos, produccion, rentabilidad. Parcial/generico, no dominio cerrado.
7. Reconciliation Service: cruce de fuentes y diferencias cuantificadas. Parcial, con tests, sin MCP.
8. Stock Control: inventario, roturas, faltantes y discrepancias. No evidenciado.
9. Hallazgos Service: dedupe, severidad, ciclo de vida, comunicacion owner. Parcial.
10. Automation / Action Engine: propuestas, aprobacion y ejecucion auditada. Parcial/conceptual; no produccion.
11. Subscription Ops: jobs recurrentes, calendario, reportes, SLA, billing. No evidenciado.

## MODELO_SUSCRIPCION_Y_SERVICIO_UNICO

Servicios unicos:

- Diagnostico inicial y ordenamiento de archivos.
- Excel con formulas.
- Macro o script puntual.
- Reparacion/limpieza de planilla.
- Conversion puntual PDF/documentos a Excel.
- Conciliacion puntual de un periodo.
- Calculo puntual de costo, margen, impuestos o produccion.

Suscripciones:

- Conciliacion recurrente bancaria/ventas/compras.
- Lectura mensual de documentos, tickets o remitos.
- Reporte periodico de hallazgos.
- Control recurrente de stock.
- Automatizaciones monitoreadas.
- Mantenimiento de modelos Excel/macros.
- Evolucion progresiva del sistema del cliente.

Regla comercial: si el problema es ocasional y acotado, vender servicio unico. Si se repite, tiene riesgo economico o requiere monitoreo, vender suscripcion.

## MAPA_REPO_REAL_VS_PRODUCTO_FINAL

| Producto final | Evidencia real en repo | Gap |
|---|---|---|
| Bot owner conversacional | Hermes documentado como operador; wrapper runtime mencionado | Falta flujo onboarding producto y tests |
| Crear trabajo desde necesidad owner | `mcp_smartpyme_bridge.py`, `OperationalPlanContract`, jobs SQLite | Falta clasificador de onboarding a plan |
| Guardar incertidumbre | `save_clarification`, `list_pending_validations`, `resolve_clarification` | Falta UX owner y owner_id efectivo |
| Ingesta documental | `DocumentIngestionService`, raw document registry, EvidenceStore | Batch, errores por archivo, retrieval formal |
| Evidencia recuperable | `get_evidence`, chunks JSONL, citation index | EvidenceRepository formal pendiente |
| Normalizacion | Documentada como pendiente | Falta contrato runtime |
| Entity resolution | Documentada como pendiente | Falta contrato runtime |
| Reconciliacion | `app/core/reconciliation/service.py`, tests | No expuesta por MCP; depende de normalizacion/entity |
| Hallazgos | `app/core/hallazgos/service.py`, tests | Falta repositorio/ciclo MCP/comunicacion |
| Comunicacion owner | Servicios legacy/parciales | Falta contrato final con evidencia |
| Accion/automatizacion | action services y execution contracts parciales | No hay adaptador real ni autorizacion productiva |
| Excel/macros | No evidenciado | Crear contrato y primer servicio |
| Stock/impuestos/produccion | No evidenciado como modulos | Definir schemas y alcance minimo |

## GAPS_CRITICOS

1. Onboarding owner no existe como contrato ejecutable.
2. Catalogo de servicios no esta conectado a `create_job`.
3. Excel/macros no tienen modulo ni tests.
4. Ingesta batch y EvidenceRepository formal estan pendientes.
5. Fact extraction y canonical rows no estan implementados como runtime cerrado.
6. Entity resolution falta y bloquea reconciliacion confiable.
7. Reconciliation no debe exponerse por MCP hasta cerrar capas previas.
8. Hallazgos no gobiernan aun el runtime MCP.
9. Stock, impuestos, produccion y rentabilidad no tienen schemas de dominio.
10. Modelo de suscripcion necesita jobs recurrentes, estados, calendario y reporte.

## ROADMAP_DIARIO_12_HITOS

1. Definir contrato `OwnerOnboardingSession` documental: preguntas, estados, salida a plan operativo.
2. Mapear catalogo de servicios a `skill_id`/estado: implemented, partial, pending, blocked.
3. Crear contrato de decision de servicio: unico vs suscripcion, con reglas medibles.
4. Endurecer `OperationalPlanContract` para aceptar `service_type`, `business_pain`, `source_types` y `delivery_level`.
5. Implementar clasificador minimo onboarding -> operational plan sin IA libre.
6. Crear job desde onboarding y verificar `get_job_status`.
7. Cerrar ingesta batch con errores por archivo y evidencia por source.
8. Crear `EvidenceRepository` local para documentos/chunks/citations.
9. Definir primer `FactCandidate` para un caso simple: conciliacion ventas/pagos o PDF a tabla.
10. Definir `CanonicalRowCandidate` y tests de trazabilidad.
11. Conectar reconciliation a canonical rows en contrato interno, sin MCP aun.
12. Convertir diferencias cuantificadas en hallazgos con repositorio y mensaje owner validable.

## TAREAS_RECOMENDADAS_PARA_HERMES_GEMINI_CODEX

Hermes proximo ciclo:

- Ejecutar una sola tarea: crear task spec para `owner_onboarding_contract_001`.
- No tocar core ni factory/control salvo que el gate lo ordene.
- Guardar evidencia en `factory/evidence/owner_onboarding_contract_001/`.

Gemini proximo ciclo:

- Definir arquitectura conceptual del onboarding: preguntas, estados comerciales, tipos de dolor, nivel de servicio y limites.
- Separar estrictamente onboarding comercial de pipeline tecnico.
- Entregar criterios de bloqueo y preguntas al owner.

Codex proximo ciclo:

- Auditar archivos reales afectados por `OperationalPlanContract` y proponer patch minimo para extender contrato solo si hay spec aprobada.
- No implementar Excel, stock, impuestos o suscripciones sin contrato previo.
- Validar con tests existentes y evidencia fisica.

## PREGUNTAS_PARA_GPT_DIRECTOR

1. Confirmar si el siguiente ciclo debe documentar onboarding o modificar contrato de plan operativo.
2. Definir primer servicio vendible: Excel simple, conversion PDF a Excel, conciliacion puntual o ingesta documental.
3. Confirmar si SmartPyme debe priorizar owner bot antes que ingestion batch.
4. Definir si el primer dominio de negocio sera conciliacion bancaria, ventas/pagos o stock.
5. Confirmar si suscripciones requieren billing/CRM ahora o solo contrato tecnico.
6. Resolver naming comercial: SmartPyme OS vs SmartPyme Core vs SmartCounter Core en superficies externas.
