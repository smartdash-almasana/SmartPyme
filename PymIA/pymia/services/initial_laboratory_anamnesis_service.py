from __future__ import annotations

from pydantic import BaseModel, Field


ESTADO_ESPERANDO_DOCUMENTACION = "esperando_documentacion"


class AnamnesisOriginaria(BaseModel):
    tenant_id: str
    canal: str
    frases_textuales: list[str] = Field(default_factory=list)
    dolores_detectados: list[str] = Field(default_factory=list)
    hipotesis_iniciales: list[str] = Field(default_factory=list)
    taxonomia_inicial: dict[str, str | None] = Field(default_factory=dict)
    documentos_pedidos: list[str] = Field(default_factory=list)
    estado_conversacional: str


class LaboratorioInicialContrato(BaseModel):
    tenant_id: str
    estado_conversacional: str
    hipotesis_a_contrastar: list[str] = Field(default_factory=list)
    evidencia_requerida: list[str] = Field(default_factory=list)
    capability: str
    tipo_documental_esperado: list[str] = Field(default_factory=list)
    campos_esperados: list[str] = Field(default_factory=list)
    nivel_confianza: str
    limite_actual: str


class InitialLaboratoryAnamnesisResult(BaseModel):
    message: str
    anamnesis: AnamnesisOriginaria
    laboratorio: LaboratorioInicialContrato


class InitialLaboratoryAnamnesisService:
    """Recepción clínica-operacional mínima para el primer tiempo lógico.

    Esta capa no diagnostica. Abre hipótesis, pide evidencia y reduce
    incertidumbre antes de derivar al pipeline documental.
    """

    _MARGIN_SIGNALS = (
        "no se si gano",
        "no sé si gano",
        "no se si estoy ganando",
        "no sé si estoy ganando",
        "perdiendo plata",
        "pierdo plata",
        "no me queda plata",
        "vendo pero",
        "vendo mucho",
        "margen",
        "rentabilidad",
        "ganancia",
        "ganando plata",
    )

    def process(
        self,
        *,
        tenant_id: str,
        channel: str,
        text: str,
    ) -> InitialLaboratoryAnamnesisResult | None:
        import uuid
        from pymia.pipeline.admission.v1.pipeline import AdmissionPipelineV1
        from pymia.pipeline.admission.v1.response_formatter import AdmissionResponseFormatterV1

        # 1. Intentar con el pipeline de admisión V1
        pipeline = AdmissionPipelineV1()
        pyme_id = uuid.uuid4()
        artifact, _ = pipeline.run(pyme_id=pyme_id, claim=text)

        message: str
        if artifact.hypotheses:
            formatter = AdmissionResponseFormatterV1()
            formatted_message = formatter.format_response(artifact)
            if formatted_message:
                message = formatted_message
                hipotesis = [h.description for h in artifact.hypotheses]
                documentos = sorted(list(set(e for h in artifact.hypotheses for e in h.evidence_required)))
            else:
                # Fallback por si el formatter falla
                documentos = sorted(list(set(e for h in artifact.hypotheses for e in h.evidence_required)))
                hipotesis = [h.description for h in artifact.hypotheses]
                message = self._build_message(documentos)
        else:
            # 2. Fallback a la lógica original si el pipeline no arroja resultados
            normalized = self._normalize(text)
            if not any(signal in normalized for signal in self._MARGIN_SIGNALS):
                return None

            documentos = [
                "ventas del período",
                "costos o facturas de compra",
                "lista de precios vigente",
                "extracto/caja si querés revisar si el problema es liquidez",
            ]
            hipotesis = [
                "margen erosionado",
                "costos desactualizados",
                "precios de venta no alineados a costo",
                "caja o liquidez mezclada con rentabilidad",
            ]
            message = self._build_message(documentos)

        anamnesis = AnamnesisOriginaria(
            tenant_id=tenant_id,
            canal=channel,
            frases_textuales=[text],
            dolores_detectados=["incertidumbre de rentabilidad"],
            hipotesis_iniciales=hipotesis,
            taxonomia_inicial={
                "rubro": None,
                "tipo_pyme": None,
                "produce_o_revende": None,
                "maneja_stock": None,
            },
            documentos_pedidos=documentos,
            estado_conversacional=ESTADO_ESPERANDO_DOCUMENTACION,
        )
        laboratorio = LaboratorioInicialContrato(
            tenant_id=tenant_id,
            estado_conversacional=ESTADO_ESPERANDO_DOCUMENTACION,
            hipotesis_a_contrastar=hipotesis,
            evidencia_requerida=documentos,
            capability="laboratorio_inicial_margen_rentabilidad",
            tipo_documental_esperado=["xlsx", "csv", "pdf", "captura"],
            campos_esperados=[
                "producto",
                "fecha",
                "cantidad",
                "precio_venta",
                "costo",
                "proveedor",
                "medio_de_cobro",
            ],
            nivel_confianza="hipotesis_abierta",
            limite_actual=(
                "No se puede afirmar rentabilidad real sin contrastar ventas "
                "contra costos, precios y caja."
            ),
        )

        return InitialLaboratoryAnamnesisResult(
            message=message,
            anamnesis=anamnesis,
            laboratorio=laboratorio,
        )

    def _build_message(self, documentos: list[str]) -> str:
        docs = "\n".join(f"- {documento}" for documento in documentos)
        return (
            "Entiendo el dolor: estás vendiendo o trabajando, pero no tenés "
            "claridad sobre si la empresa realmente gana plata.\n\n"
            "Todavía no voy a diagnosticar. Primero necesito reducir "
            "incertidumbre con evidencia.\n\n"
            "Para abrir el primer laboratorio de rentabilidad/margen, enviame "
            "si podés:\n"
            f"{docs}\n\n"
            "Con eso puedo contrastar ventas contra costos/precios y separar "
            "si el problema parece ser margen, costos desactualizados o caja."
        )

    def _normalize(self, text: str) -> str:
        replacements = {
            "á": "a",
            "é": "e",
            "í": "i",
            "ó": "o",
            "ú": "u",
            "ü": "u",
        }
        normalized = text.lower().strip()
        for source, target in replacements.items():
            normalized = normalized.replace(source, target)
        return normalized
