"""
Implementación del pipeline de admisión v1.

Este pipeline toma una narrativa inicial y la transforma en un artefacto
estructurado (DDIArtifact) que contiene síntomas, hipótesis y el estado
de admisión, de forma puramente determinística.
"""
import uuid
from app.contracts.admission_v1 import (
    SymptomNode,
    DDIArtifact,
    AdmissionState,
    HypothesisNode
)
from app.pipeline.admission.v1.heuristics import get_hypotheses_for_claim

class AdmissionPipelineV1:
    """
    Pipeline determinístico para procesar la admisión inicial de un caso PyME.
    """
    def run(self, pyme_id: uuid.UUID, claim: str) -> tuple[DDIArtifact, AdmissionState]:
        """
        Ejecuta el pipeline de admisión.

        Args:
            pyme_id: El ID de la PyME.
            claim: La narrativa o 'dolor' inicial del cliente.

        Returns:
            Un tupla conteniendo el DDIArtifact y el AdmissionState.
        """
        # 1. Crear el SymptomNode a partir del claim
        symptom = SymptomNode(claim=claim)

        # 2. Generar y puntuar hipótesis usando las heurísticas
        scored_hypotheses = get_hypotheses_for_claim(claim)
        
        hypotheses = [
            HypothesisNode(
                description=h["description"],
                evidence_required=h["evidence_required"],
                confidence_score=h["score"]
            ) for h in scored_hypotheses
        ]

        # 3. Ordenar hipótesis por score descendente
        hypotheses.sort(key=lambda h: h.confidence_score, reverse=True)

        # 4. Consolidar la evidencia requerida de todas las hipótesis
        required_evidence = set()
        for hypo in hypotheses:
            for evidence in hypo.evidence_required:
                required_evidence.add(evidence)

        # 5. Determinar el estado final de la admisión
        if hypotheses:
            admission_state = AdmissionState(
                pyme_id=pyme_id,
                state="hypotheses_generated",
                details=f"Se generaron {len(hypotheses)} hipótesis. "
                        f"La hipótesis principal es '{hypotheses[0].description}'. "
                        f"Se requiere la siguiente evidencia: {sorted(list(required_evidence))}"
            )
        else:
            admission_state = AdmissionState(
                pyme_id=pyme_id,
                state="symptoms_captured",
                details="Se capturó un síntoma pero no se generaron hipótesis automáticas."
            )
        
        # 6. Crear el artefacto DDI y asignar hipótesis primaria
        primary_hypo_id = hypotheses[0].node_id if hypotheses else None
        artifact = DDIArtifact(
            pyme_id=pyme_id,
            symptoms=[symptom],
            hypotheses=hypotheses,
            primary_hypothesis_id=primary_hypo_id
        )

        return artifact, admission_state
