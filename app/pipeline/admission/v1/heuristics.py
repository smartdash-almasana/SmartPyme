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

    # Comprobar si el claim activa el cluster de síntomas de rentabilidad
    has_action = any(verb in normalized_claim for verb in PROFITABILITY_SYMPTOM_CLUSTERS["ACTION_VERBS"])
    has_money_noun = any(noun in normalized_claim for noun in PROFITABILITY_SYMPTOM_CLUSTERS["MONEY_NOUNS"])
    has_pain = any(pain in normalized_claim for pain in PROFITABILITY_SYMPTOM_CLUSTERS["PAIN_INDICATORS"])

    # Lógica de activación: necesita una acción y un indicador de dolor, o un sustantivo de dinero y un indicador de dolor.
    if (has_action and has_pain) or (has_money_noun and has_pain):
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
