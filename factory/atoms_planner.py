from dataclasses import dataclass

from factory.atoms_catalog import resolver_atomo_por_objetivo


@dataclass(frozen=True)
class PlannerOutput:
    atomo_actual: str
    siguiente_atomo_sugerido: str | None
    secuencia_sugerida: list[str]
    origen_planificacion: str
    area: str


SECUENCIAS_EXPLICITAS: dict[str, list[str]] = {
    "atomo_core_hallazgo_smoke": [
        "atomo_core_hallazgo_smoke",
        "atomo_pipeline_flujo_smoke",
        "atomo_catalogo_contratos",
    ],
    "atomo_pipeline_flujo_smoke": [
        "atomo_pipeline_flujo_smoke",
        "atomo_catalogo_contratos",
    ],
    "atomo_catalogo_contratos": [
        "atomo_catalogo_contratos",
        "atomo_factoria_contratos",
    ],
}


def planificar_secuencia_atomica(objetivo: str) -> PlannerOutput:
    atomo = resolver_atomo_por_objetivo(objetivo)
    if atomo:
        secuencia = SECUENCIAS_EXPLICITAS.get(atomo.atomo_id)
        if secuencia:
            secuencia_corta = secuencia[:4]
            siguiente = secuencia_corta[1] if len(secuencia_corta) > 1 else None
            return PlannerOutput(
                atomo_actual=secuencia_corta[0],
                siguiente_atomo_sugerido=siguiente,
                secuencia_sugerida=secuencia_corta,
                origen_planificacion="planner",
                area=atomo.area,
            )
        return PlannerOutput(
            atomo_actual=atomo.atomo_id,
            siguiente_atomo_sugerido=None,
            secuencia_sugerida=[atomo.atomo_id],
            origen_planificacion="fallback",
            area=atomo.area,
        )

    return PlannerOutput(
        atomo_actual="fallback_heuristico",
        siguiente_atomo_sugerido=None,
        secuencia_sugerida=["fallback_heuristico"],
        origen_planificacion="fallback",
        area="factoria",
    )
