"""Formatter deterministico para respuestas del Laboratorio Inicial PyME."""

from app.contracts.admission_v1 import DDIArtifact, HypothesisNode


class AdmissionResponseFormatterV1:
    """Convierte un DDIArtifact en mensaje sobrio para el duenio."""

    def format_response(self, artifact: DDIArtifact) -> str | None:
        if not artifact.symptoms or not artifact.hypotheses:
            return None

        primary_hypothesis = self._get_primary_hypothesis(artifact)
        if primary_hypothesis is None:
            return None

        other_hypotheses = [
            hypothesis.description
            for hypothesis in artifact.hypotheses
            if hypothesis.node_id != primary_hypothesis.node_id
        ]

        all_evidence = sorted(
            {
                evidence
                for hypothesis in artifact.hypotheses
                for evidence in hypothesis.evidence_required
            }
        )

        parts = [
            "Registré este síntoma operacional: "
            + artifact.symptoms[0].claim
            + ".",
            "Hipótesis inicial prioritaria:\n"
            + primary_hypothesis.description.lower()
            + ".",
        ]

        if other_hypotheses:
            parts.append(
                "También quedan abiertas:\n"
                + ", ".join(h.lower() for h in other_hypotheses)
                + "."
            )

        if all_evidence:
            parts.append(
                "Para confirmar o refutar estas hipótesis necesito:\n"
                + ", ".join(all_evidence)
                + "."
            )

        parts.append(
            "Cuando reciba esa evidencia, voy a construir la primera línea "
            "de base del Laboratorio Inicial PyME."
        )

        return "\n\n".join(parts)

    def _get_primary_hypothesis(
        self,
        artifact: DDIArtifact,
    ) -> HypothesisNode | None:
        primary = [
            hypothesis
            for hypothesis in artifact.hypotheses
            if getattr(hypothesis, "is_primary", False)
        ]
        if primary:
            return primary[0]

        return max(
            artifact.hypotheses,
            key=lambda hypothesis: getattr(hypothesis, "confidence_score", 0.0),
            default=None,
        )
