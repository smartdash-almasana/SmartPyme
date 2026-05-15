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
    matched_keywords: list[str]

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
    "PAIN_INDICATORS": {"no queda plata", "no queda", "no queda nada", "desaparece", "no vemos ganancias", "no sé si gano", "no se si gano", "no sé si deja margen"}
}

# Clúster de palabras clave para detectar la intención de "problema de stock/inventario"
INVENTORY_SYMPTOM_CLUSTERS = {
    "NOUNS": {"stock", "mercadería", "mercaderia", "productos"},
    "PAIN_INDICATORS": {"stock parado", "no rota", "falta de stock", "falta", "productos clavados", "clavado", "no sale", "venta cortada"}
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

def _find_matches(normalized_claim: str, keywords: set[str]) -> list[str]:
    return [kw for kw in keywords if kw in normalized_claim]

def get_hypotheses_for_claim(claim: str) -> list[ScoredHypothesis]:
    """
    Genera una lista de hipótesis puntuadas basada en un claim narrativo.
    """
    normalized_claim = _normalize(claim)
    all_scored_hypotheses: list[ScoredHypothesis] = []

    # --- Scoring Cluster de Rentabilidad ---
    profit_matched_keywords: list[str] = []
    profit_score = 0.0

    action_matches = _find_matches(normalized_claim, PROFITABILITY_SYMPTOM_CLUSTERS["ACTION_VERBS"])
    money_matches = _find_matches(normalized_claim, PROFITABILITY_SYMPTOM_CLUSTERS["MONEY_NOUNS"])
    pain_matches = _find_matches(normalized_claim, PROFITABILITY_SYMPTOM_CLUSTERS["PAIN_INDICATORS"])

    if (action_matches or money_matches) and pain_matches:
        if action_matches:
            profit_score += KEYWORD_WEIGHTS["ACTION_VERBS"]
            profit_matched_keywords.extend(action_matches)
        if money_matches:
            profit_score += KEYWORD_WEIGHTS["MONEY_NOUNS"]
            profit_matched_keywords.extend(money_matches)
        if pain_matches:
            profit_score += KEYWORD_WEIGHTS["PROFIT_PAIN"]
            profit_matched_keywords.extend(pain_matches)

        for hypo in PROFIT_HYPOTHESES:
            all_scored_hypotheses.append({
                "description": hypo["description"],
                "evidence_required": hypo["evidence_required"],
                "score": profit_score,
                "matched_keywords": sorted(list(set(profit_matched_keywords)))
            })

    # --- Scoring Cluster de Inventario ---
    inventory_matched_keywords: list[str] = []
    inventory_score = 0.0

    noun_matches = _find_matches(normalized_claim, INVENTORY_SYMPTOM_CLUSTERS["NOUNS"])
    inv_pain_matches = _find_matches(normalized_claim, INVENTORY_SYMPTOM_CLUSTERS["PAIN_INDICATORS"])

    if noun_matches and inv_pain_matches:
        inventory_score += KEYWORD_WEIGHTS["INVENTORY_NOUNS"]
        inventory_matched_keywords.extend(noun_matches)
        inventory_score += KEYWORD_WEIGHTS["INVENTORY_PAIN"]
        inventory_matched_keywords.extend(inv_pain_matches)

        for hypo in INVENTORY_HYPOTHESES:
            all_scored_hypotheses.append({
                "description": hypo["description"],
                "evidence_required": hypo["evidence_required"],
                "score": inventory_score,
                "matched_keywords": sorted(list(set(inventory_matched_keywords)))
            })

    return all_scored_hypotheses
