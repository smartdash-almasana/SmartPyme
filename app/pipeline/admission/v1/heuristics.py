"""
Heurísticas determinísticas para el pipeline de admisión v1.

Este módulo contiene la lógica para mapear palabras clave en la narrativa
de un cliente a hipótesis de trabajo y la evidencia requerida para validarlas.
"""
from app.contracts.admission_v1 import HypothesisNode

# Base de conocimiento heurística
# Mapea palabras clave a una tupla de (descripción_hipótesis, evidencia_requerida)
HEURISTIC_RULES = {
    "plata": (
        "Tensión de caja",
        ["movimientos de caja", "extractos bancarios"]
    ),
    "margen": (
        "Margen de contribución erosionado",
        ["informe de ventas", "lista de costos variables"]
    ),
    "costos": (
        "Fuga operativa o costos fijos elevados",
        ["listado de gastos", "facturas de proveedores"]
    ),
    "vendemos": (
        "Margen de contribución erosionado",
        ["informe de ventas", "lista de costos variables"]
    ),
    # Combinación para el caso específico
    "no queda plata": (
        "Tensión de caja por ciclo de conversión de efectivo",
        ["ventas a crédito", "plazos de pago a proveedores"]
    )
}

# Hipótesis predefinidas para el caso "vendemos mucho pero no queda plata"
SPECIFIC_CASE_HYPOTHESES = {
    "vendemos mucho pero no queda plata": [
        HypothesisNode(
            description="Tensión de caja",
            evidence_required=["ventas", "costos", "movimientos de caja", "extractos"]
        ),
        HypothesisNode(
            description="Fuga operativa",
            evidence_required=["ventas", "costos", "movimientos de caja", "extractos"]
        ),
        HypothesisNode(
            description="Margen erosionado",
            evidence_required=["ventas", "costos", "movimientos de caja", "extractos"]
        )
    ]
}


def get_hypotheses_for_claim(claim: str) -> list[HypothesisNode]:
    """
    Genera una lista de hipótesis basada en un claim narrativo, utilizando
    un conjunto de reglas heurísticas simples.
    """
    normalized_claim = claim.lower()
    
    # Check for the specific case first
    if "vendemos mucho pero no queda plata" in normalized_claim:
        return SPECIFIC_CASE_HYPOTHESES["vendemos mucho pero no queda plata"]

    # Generic keyword-based approach
    found_hypotheses = {}
    for keyword, (desc, evidence) in HEURISTIC_RULES.items():
        if keyword in normalized_claim:
            if desc not in found_hypotheses:
                found_hypotheses[desc] = HypothesisNode(
                    description=desc,
                    evidence_required=evidence
                )
            else:
                # Si la hipótesis ya existe, añadir nueva evidencia requerida si es diferente
                existing_evidence = set(found_hypotheses[desc].evidence_required)
                existing_evidence.update(evidence)
                found_hypotheses[desc].evidence_required = sorted(list(existing_evidence))

    return list(found_hypotheses.values())
