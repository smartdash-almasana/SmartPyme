"""
Heurísticas determinísticas para el pipeline de admisión v1.

Este módulo contiene la lógica para mapear palabras clave en la narrativa
de un cliente a hipótesis de trabajo y la evidencia requerida para validarlas.
"""
from app.contracts.admission_v1 import HypothesisNode

# Clúster de palabras clave para detectar la intención de "problema de rentabilidad/caja"
PROFITABILITY_SYMPTOM_CLUSTERS = {
    "ACTION_VERBS": {"vendo", "vendemos", "facturo", "trabajamos", "entra"},
    "MONEY_NOUNS": {"plata", "nada", "ganancias", "margen"},
    "PAIN_INDICATORS": {"no queda", "desaparece", "no vemos", "no sé si gano", "no se si gano", "no sé si deja", "no se si deja"}
}

# Clúster de palabras clave para detectar la intención de "problema de stock/inventario"
INVENTORY_SYMPTOM_CLUSTERS = {
    "NOUNS": {"stock", "mercadería", "mercaderia", "productos"},
    "PAIN_INDICATORS": {"parado", "no rota", "falta", "clavados", "no sale", "corta"}
}


def _normalize(text: str) -> str:
    replacements = {
        "á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u", "ü": "u",
    }
    normalized = text.lower().strip()
    for source, target in replacements.items():
        normalized = normalized.replace(source, target)
    return normalized

def get_hypotheses_for_claim(claim: str) -> list[HypothesisNode]:
    """
    Genera una lista de hipótesis basada en un claim narrativo, utilizando
    un sistema de clusters de palabras clave.
    """
    normalized_claim = _normalize(claim)

    # --- Cluster de Inventario ---
    has_inventory_noun = any(noun in normalized_claim for noun in INVENTORY_SYMPTOM_CLUSTERS["NOUNS"])
    has_inventory_pain = any(pain in normalized_claim for pain in INVENTORY_SYMPTOM_CLUSTERS["PAIN_INDICATORS"])

    if has_inventory_noun and has_inventory_pain:
        return [
            HypothesisNode(
                description="Stock inmovilizado",
                evidence_required=["inventario actual", "ventas por producto", "compras"]
            ),
            HypothesisNode(
                description="Asincronía inventario-demanda",
                evidence_required=["inventario actual", "ventas por producto", "rotación por SKU"]
            ),
            HypothesisNode(
                description="Quiebre de stock",
                evidence_required=["ventas por producto", "inventario actual"]
            ),
            HypothesisNode(
                description="Capital atrapado en inventario",
                evidence_required=["inventario actual", "compras", "lista de precios"]
            )
        ]

    # --- Cluster de Rentabilidad ---
    has_profit_action = any(verb in normalized_claim for verb in PROFITABILITY_SYMPTOM_CLUSTERS["ACTION_VERBS"])
    has_profit_money_noun = any(noun in normalized_claim for noun in PROFITABILITY_SYMPTOM_CLUSTERS["MONEY_NOUNS"])
    has_profit_pain = any(pain in normalized_claim for pain in PROFITABILITY_SYMPTOM_CLUSTERS["PAIN_INDICATORS"])

    if (has_profit_action and has_profit_pain) or (has_profit_money_noun and has_profit_pain):
        return [
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
                evidence_required=["ventas", "costos", "movimientos de caja", "extractos", "lista de precios si aplica"]
            )
        ]

    return []
