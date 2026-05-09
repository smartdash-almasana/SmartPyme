# SMARTPYME SmartGraph — Arquitectura Conceptual

## Propósito
SmartGraph provee memoria estructural para observaciones, entidades, relaciones y claims del dominio PyME, preservando la separación con el core clínico-operacional.

## Principios
- Separación estricta: SmartGraph no reemplaza runtime principal.
- Persistencia soberana: SQL/Supabase como fuente durable.
- Fail-closed: sin tenant válido no hay operación.
- Trazabilidad epistemológica: claim_type + claim_status + evidencia + revisión humana.
- No LLM direct writes.

## Modelo conceptual
- **Node**: entidad canónica (empresa, cliente, proveedor, producto, síntoma, patología, etc.).
- **Edge**: relación tipada entre nodos con claim_type y confidence.
- **Alias**: variantes lingüísticas/operativas para resolución canónica.
- **Claim**: afirmación explícita con estado de soporte y gating humano.

## Invariantes clave
1. Toda fila tiene `tenant_id`.
2. `claim_type` distingue extraído vs inferido/ambiguo/hipótesis/validado.
3. `confidence` en [0,1] cuando aplica.
4. `evidence_ids` preserva trazabilidad de soporte.
5. `requires_human_review=true` bloquea `SUPPORTED` hasta revisión explícita.

## Fronteras del sistema
- Dentro de SmartGraph: persistencia, consulta, export y subgrafo de activación a nivel repositorio.
- Fuera de SmartGraph (por ahora): EntityResolutionService y SmartGraphActivationEngine de alto nivel.

## Nota sobre Graphify
Graphify puede inspirar modelado o pruebas exploratorias, pero no forma parte del runtime productivo de SmartPyme.
