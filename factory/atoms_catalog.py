from dataclasses import dataclass


@dataclass(frozen=True)
class FactoryAtom:
    atomo_id: str
    nombre: str
    area: str
    writer_objetivo: str
    validator_objetivo: str
    match_terms: tuple[str, ...]


CATALOGO_ATOMOS: tuple[FactoryAtom, ...] = (
    FactoryAtom(
        atomo_id="atomo_core_hallazgo_smoke",
        nombre="Smoke de dominio core",
        area="core",
        writer_objetivo="writer_core",
        validator_objetivo="validator_tests",
        match_terms=("app/core/", "hallazgo", "core"),
    ),
    FactoryAtom(
        atomo_id="atomo_pipeline_flujo_smoke",
        nombre="Smoke de flujo de orquestacion",
        area="pipeline",
        writer_objetivo="writer_pipeline",
        validator_objetivo="validator_tests",
        match_terms=("app/orchestration/", "pipeline", "flujo"),
    ),
    FactoryAtom(
        atomo_id="atomo_catalogo_contratos",
        nombre="Contrato de catalogo tipado",
        area="catalogo",
        writer_objetivo="writer_core",
        validator_objetivo="validator_contracts",
        match_terms=("catálogo", "catalogo", "tipado", "contrato"),
    ),
    FactoryAtom(
        atomo_id="atomo_factoria_contratos",
        nombre="Contrato base de factoria",
        area="factoria",
        writer_objetivo="writer_core",
        validator_objetivo="validator_contracts",
        match_terms=("factoria", "factory"),
    ),
)


def resolver_atomo_por_objetivo(objetivo: str) -> FactoryAtom | None:
    objetivo_lower = objetivo.lower()
    for atomo in CATALOGO_ATOMOS:
        if any(match in objetivo_lower for match in atomo.match_terms):
            return atomo
    return None


def resolver_atomo_por_id(atomo_id: str) -> FactoryAtom | None:
    for atomo in CATALOGO_ATOMOS:
        if atomo.atomo_id == atomo_id:
            return atomo
    return None
