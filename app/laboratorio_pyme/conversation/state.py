"""Estado conversacional del motor clínico SmartPyme.

Un estado representa la memoria viva de una sesión con un dueño de PyME.
No es un formulario: es un expediente clínico-operacional en construcción.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class FaseConversacion(str, Enum):
    """Fases del protocolo clínico de investigación."""

    ANAMNESIS_GENERAL = "anamnesis_general"
    FOCO_SINTOMAS = "foco_sintomas"
    RECOLECCION_EVIDENCIA = "recoleccion_evidencia"
    ANALISIS_HIPOTESIS = "analisis_hipotesis"
    BLOQUEO_POR_EVIDENCIA = "bloqueo_por_evidencia"


@dataclass
class HipotesisActiva:
    """Una hipótesis activada con su peso de evidencia."""

    codigo: str
    nombre: str
    peso: float
    dimension: str
    evidencia_faltante: list[str] = field(default_factory=list)
    evidencia_confirmada: list[str] = field(default_factory=list)
    subsistemas_afectados: list[str] = field(default_factory=list)

    def reforzar(self, nuevo_peso: float) -> None:
        self.peso = min(1.0, max(self.peso, round(nuevo_peso, 4)))


@dataclass
class ConversationState:
    """Estado completo de una sesión investigativa con el dueño."""

    cliente_id: str
    fase: FaseConversacion = FaseConversacion.ANAMNESIS_GENERAL
    dolor_principal: str | None = None
    hipotesis_activas: list[HipotesisActiva] = field(default_factory=list)
    evidencia_requerida: list[str] = field(default_factory=list)
    evidencia_confirmada: list[str] = field(default_factory=list)
    datos_conocidos: list[dict[str, Any]] = field(default_factory=list)
    incertidumbres: list[str] = field(default_factory=list)
    historial_preguntas: list[str] = field(default_factory=list)
    historial_mensajes: list[str] = field(default_factory=list)
    dimension_foco: str | None = None
    ultima_pregunta: str | None = None

    @property
    def estado(self) -> str:
        return self.fase.value

    def registrar_mensaje(self, mensaje: str) -> None:
        texto = mensaje.strip()
        if not texto:
            return
        self.historial_mensajes.append(texto)
        if self.dolor_principal is None:
            self.dolor_principal = texto

    def hipotesis_por_codigo(self, codigo: str) -> HipotesisActiva | None:
        return next((h for h in self.hipotesis_activas if h.codigo == codigo), None)

    def agregar_evidencia_requerida(self, item: str) -> None:
        if item not in self.evidencia_requerida and item not in self.evidencia_confirmada:
            self.evidencia_requerida.append(item)

    def marcar_evidencia_recibida(self, item: str) -> None:
        if item in self.evidencia_requerida:
            self.evidencia_requerida.remove(item)
        if item not in self.evidencia_confirmada:
            self.evidencia_confirmada.append(item)
        self.datos_conocidos.append({"tipo": item, "estado": "recibido"})

        for hipotesis in self.hipotesis_activas:
            if item in hipotesis.evidencia_faltante:
                hipotesis.evidencia_faltante.remove(item)
            if item not in hipotesis.evidencia_confirmada:
                hipotesis.evidencia_confirmada.append(item)

    def pregunta_ya_hecha(self, pregunta: str) -> bool:
        normalizada = pregunta.strip()
        return any(normalizada == p.strip() for p in self.historial_preguntas)

    def registrar_pregunta(self, pregunta: str) -> None:
        self.ultima_pregunta = pregunta
        if not self.pregunta_ya_hecha(pregunta):
            self.historial_preguntas.append(pregunta)

    def activar_o_reforzar_hipotesis(
        self,
        *,
        codigo: str,
        nombre: str,
        peso: float,
        dimension: str,
        evidencia_faltante: list[str],
        subsistemas_afectados: list[str] | None = None,
    ) -> None:
        activa = self.hipotesis_por_codigo(codigo)
        if activa is None:
            activa = HipotesisActiva(
                codigo=codigo,
                nombre=nombre,
                peso=peso,
                dimension=dimension,
                evidencia_faltante=list(evidencia_faltante),
                subsistemas_afectados=list(subsistemas_afectados or []),
            )
            self.hipotesis_activas.append(activa)
        else:
            activa.reforzar(peso)
            for item in evidencia_faltante:
                if item not in activa.evidencia_faltante and item not in activa.evidencia_confirmada:
                    activa.evidencia_faltante.append(item)

        for item in evidencia_faltante:
            self.agregar_evidencia_requerida(item)

    def actualizar_fase(self) -> None:
        if not self.hipotesis_activas:
            self.fase = FaseConversacion.FOCO_SINTOMAS if self.dolor_principal else FaseConversacion.ANAMNESIS_GENERAL
        elif self.evidencia_requerida:
            self.fase = FaseConversacion.RECOLECCION_EVIDENCIA
        else:
            self.fase = FaseConversacion.ANALISIS_HIPOTESIS

    def get(self, key: str, default: Any = None) -> Any:
        return getattr(self, key, default)

    def __getitem__(self, key: str) -> Any:
        if key == "estado":
            return self.estado
        return getattr(self, key)

    def __setitem__(self, key: str, value: Any) -> None:
        if key == "estado":
            self.fase = FaseConversacion(value)
            return
        setattr(self, key, value)


def crear_estado_inicial(cliente_id: str) -> ConversationState:
    return ConversationState(cliente_id=cliente_id)
