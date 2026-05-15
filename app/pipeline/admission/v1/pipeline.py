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
    AdmissionState
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

        # 2. Generar hipótesis usando las heurísticas
        hypotheses = get_hypotheses_for_claim(claim)

        # 3. Consolidar la evidencia requerida de todas las hipótesis
        required_evidence = set()
        for hypo in hypotheses:
            for evidence in hypo.evidence_required:
                required_evidence.add(evidence)

        # 4. Determinar el estado final de la admisión
        if hypotheses:
            admission_state = AdmissionState(
                pyme_id=pyme_id,
                state="hypotheses_generated",
                details=f"Se generaron {len(hypotheses)} hipótesis. "
                        f"Se requiere la siguiente evidencia: {sorted(list(required_evidence))}"
            )
        else:
            admission_state = AdmissionState(
                pyme_id=pyme_id,
                state="symptoms_captured",
                details="Se capturó un síntoma pero no se generaron hipótesis automáticas."
            )
        
        # 5. Crear el artefacto DDI
        artifact = DDIArtifact(
            pyme_id=pyme_id,
            symptoms=[symptom],
            hypotheses=hypotheses,
        )

        return artifact, admission_state
