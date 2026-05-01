from __future__ import annotations

import unicodedata
from typing import Any

from app.services.operational_taxonomy_service import OperationalTaxonomyService


class OperationalTaxonomyMatcherService:
    def __init__(self, taxonomy_service: OperationalTaxonomyService | None = None) -> None:
        self.taxonomy_service = taxonomy_service or OperationalTaxonomyService()

    def match(self, owner_message: str, limit: int = 3) -> list[dict[str, Any]]:
        if not owner_message.strip():
            return []

        normalized_msg = self._normalize(owner_message)
        candidates = []

        for item in self.taxonomy_service.list_items():
            score = 0
            matched_signals = []

            # 1. Keywords CLAE (+5)
            keywords_clae = item.get("actividad_oficial_referencia", {}).get("keywords_clae", [])
            for kw in keywords_clae:
                norm_kw = self._normalize(kw)
                if norm_kw and norm_kw in normalized_msg:
                    score += 5
                    matched_signals.append(f"keyword_clae: {kw}")

            # 2. Senales Anamnesis (+4)
            senales = item.get("senales_anamnesis", [])
            for s in senales:
                norm_s = self._normalize(s)
                if norm_s and norm_s in normalized_msg:
                    score += 4
                    matched_signals.append(f"senal: {s}")

            # 3. Tipo Operativo Words (+2)
            tipo_op = item.get("tipo_operativo", "")
            for word in tipo_op.replace("_", " ").split():
                norm_word = self._normalize(word)
                if norm_word and len(norm_word) > 2 and norm_word in normalized_msg:
                    score += 2
                    matched_signals.append(f"tipo_word: {word}")

            # 4. Familia Smartpyme (+1)
            familia = item.get("familia_smartpyme", "")
            norm_familia = self._normalize(familia)
            if norm_familia and norm_familia in normalized_msg:
                score += 1
                matched_signals.append(f"familia: {familia}")

            if score > 0:
                candidates.append({
                    "item_id": item["id"],
                    "tipo_operativo": item["tipo_operativo"],
                    "familia_smartpyme": item["familia_smartpyme"],
                    "score": score,
                    "matched_signals": sorted(list(set(matched_signals))),
                    "suggested_questions": item["preguntas_al_dueno"],
                    "required_data": item["datos_minimos_a_pedir"],
                })

        # Sort by score descending
        candidates.sort(key=lambda x: x["score"], reverse=True)

        return candidates[:limit]

    def _normalize(self, text: str) -> str:
        if not text:
            return ""
        # Lowercase
        text = text.lower()
        # Remove accents
        text = "".join(
            c for c in unicodedata.normalize("NFKD", text)
            if not unicodedata.combining(c)
        )
        return text
