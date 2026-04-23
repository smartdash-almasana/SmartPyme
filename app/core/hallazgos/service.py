from app.core.hallazgos.models import Hallazgo

def crear_hallazgo(id: str, descripcion: str) -> Hallazgo:
    return Hallazgo(id=id, descripcion=descripcion)
