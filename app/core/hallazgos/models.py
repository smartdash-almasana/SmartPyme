from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class Hallazgo:
    id: str
    descripcion: str
