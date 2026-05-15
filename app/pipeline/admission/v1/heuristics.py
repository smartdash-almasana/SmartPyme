"""
Heurísticas determinísticas para el pipeline de admisión v1.

Este módulo contiene la lógica para mapear palabras clave en la narrativa
de un cliente a hipótesis de trabajo y la evidencia requerida para validarlas.
"""
from typing import TypedDict, Any

class ScoredHypothesis(TypedDict):
    description: str
    evidence_required: list[str]
    score: float

# Pesos para la puntuación de clusters
KEYWORD_WEIGHTS = {
    "ACTION_VERBS": 1.0,
    "MONEY_NOUNS": 1.5,
    "PROFIT_PAIN": 2.0,
    "INVENTORY_NOUNS": 1.5,
    "INVENTORY_PAIN": 2.0,
}

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

PROFIT_HYPOTHESES = [
    {"description": "Tensión de caja", "evidence_required": ["ventas", "costos", "movimientos de caja", "extractos"]},
    {"description": "Fuga operativa", "evidence_required": ["ventas", "costos", "movimientos de caja", "extractos"]},
    {"description": "Margen erosionado", "evidence_required": ["ventas", "costos", "movimientos de caja", "extractos", "lista de precios si aplica"]}
]

INVENTORY_HYPOTHESES = [
    {"description": "Stock inmovilizado", "evidence_required": ["inventario actual", "ventas por producto", "compras"]},
    {"description": "Asincronía inventario-demanda", "evidence_required": ["inventario actual", "ventas por producto", "rotación por SKU"]},
    {"description": "Quiebre de stock", "evidence_required": ["ventas por producto", "inventario actual"]},
    {"description": "Capital atrapado en inventario", "evidence_required": ["inventario actual", "compras", "lista de precios"]}
]

def _normalize(text: str) -> str:
    replacements = {
        "á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u", "ü": "u",
    }
    normalized = text.lower().strip()
    for source, target in replacements.items():
        normalized = normalized.replace(source, target)
    return normalized

def get_hypotheses_for_claim(claim: str) -> list[ScoredHypothesis]:
    """
    Genera una lista de hipótesis puntuadas basada en un claim narrativo.
    """
    normalized_claim = _normalize(claim)
    all_scored_hypotheses: list[ScoredHypothesis] = []

    # --- Scoring Cluster de Rentabilidad ---
    has_profit_action = any(verb in normalized_claim for verb in PROFITABILITY_SYMPTOM_CLUSTERS["ACTION_VERBS"])
    has_profit_money_noun = any(noun in normalized_claim for noun in PROFITABILITY_SYMPTOM_CLUSTERS["MONEY_NOUNS"])
    has_profit_pain = any(pain in normalized_claim for pain in PROFITABILITY_SYMPTOM_CLUSTERS["PAIN_INDICATORS"])
    
    if (has_profit_action or has_profit_money_noun) and has_profit_pain:
        profit_score = 0.0
        if has_profit_action:
            profit_score += KEYWORD_WEIGHTS["ACTION_VERBS"]
        if has_profit_money_noun:
            profit_score += KEYWORD_WEIGHTS["MONEY_NOUNS"]
        if has_profit_pain:
            profit_score += KEYWORD_WEIGHTS["PROFIT_PAIN"]

        for hypo in PROFIT_HYPOTHESES:
            all_scored_hypotheses.append({
                "description": hypo["description"],
                "evidence_required": hypo["evidence_required"],
                "score": profit_score
            })

    # --- Scoring Cluster de Inventario ---
    inventory_score = 0.0
    if any(noun in normalized_claim for noun in INVENTORY_SYMPTOM_CLUSTERS["NOUNS"]):
        inventory_score += KEYWORD_WEIGHTS["INVENTORY_NOUNS"]
    if any(pain in normalized_claim for pain in INVENTORY_SYMPTOM_CLUSTERS["PAIN_INDICATORS"]):
        inventory_score += KEYWORD_WEIGHTS["INVENTORY_PAIN"]

    if inventory_score > 0:
        for hypo in INVENTORY_HYPOTHESES:
            all_scored_hypotheses.append({
                "description": hypo["description"],
                "evidence_required": hypo["evidence_required"],
                "score": inventory_score
            })

    return all_scored_hypotheses
