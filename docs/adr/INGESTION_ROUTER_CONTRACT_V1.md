# ADR: Protocolo de Enrutamiento de Ingesta (Bem vs Internal)

**Estado:** APROBADO TÉCNICO
**Componente:** `app.core.ingestion.EvidenceRouter`

## 1. Lógica del Filtro (Decision Matrix)

El sistema evaluará cada pieza de evidencia adjunta bajo el siguiente contrato:

```python
from pydantic import BaseModel
from enum import Enum

class IngestionRoute(str, Enum):
    BEM_AI = "bem_ai"           # Extracción, Curaduría y Normalización
    INTERNAL_FACT = "internal"  # Ingesta directa al Kernel (Datos ya limpios)
    NARRATIVE = "narrative"     # Procesamiento conversacional (Hermes Memory)

class EvidenceTriage(BaseModel):
    evidence_id: str
    file_extension: str
    mime_type: str
    expected_schema: str        # Ej: "invoice_v1", "bank_statement", "human_claim"
    entropy_level: float        # Calculado: 0.0 (estructurado) a 1.0 (caos total)
    
    def get_route(self) -> IngestionRoute:
        if self.mime_type in ["application/pdf", "image/jpeg", "image/png"]:
            return IngestionRoute.BEM_AI
        if self.file_extension in [".xlsx", ".xls", ".csv"] and self.entropy_level > 0.3:
            return IngestionRoute.BEM_AI
        if self.expected_schema == "human_claim":
            return IngestionRoute.NARRATIVE
        return IngestionRoute.INTERNAL_FACT
```

## 2. Flujo de Ejecución

1. **Captura:** El dueño adjunta un documento en la interfaz.
2. **Pre-Auditoría:** SmartPyme analiza metadata (MimeType y Entropía).
3. **Routing:**
   - Si es **BEM_AI**: Se invoca el workflow correspondiente en Bem (ej: `extract-invoice`). Bem devuelve el Fact curado.
   - Si es **INTERNAL**: Se mapea directamente al motor de Polars del Kernel.
   - Si es **NARRATIVE**: Se procesa como un `SymptomNode`.

## 3. Beneficios Arquitectónicos
- **Costo-Eficiencia:** Solo pagamos tokens de Bem para documentos que realmente requieren visión artificial o limpieza profunda.
- **Pureza del Kernel:** El Kernel solo recibe Facts certificados (ya sea por la validación de Bem o por origen API estructurado).
- **Soberanía:** Los documentos internos (notas del sistema) no tocan APIs externas.
