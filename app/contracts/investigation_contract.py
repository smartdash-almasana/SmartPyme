"""
Contratos Pydantic — Capa 2: Activación de Conocimiento e Investigación
TS_020_001_CONTRATOS_ACTIVACION_INVESTIGATIVA

Modelos de datos mínimos para representar InvestigationGraph,
InvestigationPlan y OperationalCaseCandidate.

Principios:
  - Una demanda activa un grafo, no una respuesta.
  - Capa 2 no diagnostica ni ejecuta acciones.
  - Toda fórmula declara variables requeridas.
  - Toda variable requerida se mapea contra evidencia disponible o gap.
  - El output es OperationalCaseCandidate, no OperationalCase.

Documento rector:
  docs/product/SMARTPYME_CAPA_02_ACTIVACION_CONOCIMIENTO_INVESTIGACION.md
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import BaseModel, Field, field_validator


# ---------------------------------------------------------------------------
# Tipos literales
# ---------------------------------------------------------------------------

NodeType = Literal[
    "SymptomNode",
    "PathologyNode",
    "FormulaNode",
    "VariableNode",
    "EvidenceNode",
    "GapNode",
    "KnowledgeToolNode",
]
"""
Tipos de nodos del grafo investigativo.

SymptomNode      → síntoma expresado por el dueño.
PathologyNode    → patología operativa candidata.
FormulaNode      → fórmula o método investigativo.
VariableNode     → variable requerida por una fórmula.
EvidenceNode     → evidencia disponible que soporta una variable.
GapNode          → variable faltante, ambigua o insuficiente.
KnowledgeToolNode → herramienta conceptual, matemática o algorítmica.
"""

EdgeType = Literal[
    "TRIGGERS",
    "REQUIRES",
    "SUPPORTED_BY",
    "MISSING",
    "ASSOCIATED_WITH",
    "IMPACTS",
    "PRIORITIZES",
    "USES_TOOL",
    "HAS_GAP",
    "DEPENDS_ON",
]
"""
Tipos de relaciones entre nodos del grafo investigativo.

TRIGGERS       → síntoma activa patología candidata.
REQUIRES       → fórmula/patología requiere variable.
SUPPORTED_BY   → variable soportada por evidencia disponible.
MISSING        → variable requerida no disponible.
ASSOCIATED_WITH → patología relacionada con otra.
IMPACTS        → patología puede impactar otra.
PRIORITIZES    → ruta prioriza un nodo sobre otro.
USES_TOOL      → ruta requiere herramienta auxiliar.
HAS_GAP        → nodo tiene brecha de evidencia.
DEPENDS_ON     → dependencia general entre nodos.
"""

CandidateStatus = Literal[
    "READY_TO_INVESTIGATE",
    "PARTIAL_EVIDENCE",
    "BLOCKED_MISSING_VARIABLES",
    "PENDING_OWNER_VALIDATION",
]
"""
Estado del OperationalCaseCandidate.

READY_TO_INVESTIGATE      → evidencia suficiente para investigar.
PARTIAL_EVIDENCE          → evidencia parcial; investigación con alcance limitado.
BLOCKED_MISSING_VARIABLES → faltan variables críticas; no se puede investigar.
PENDING_OWNER_VALIDATION  → candidato listo pero requiere validación del dueño.
"""

GapPriority = Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
"""
Prioridad de una brecha de evidencia.

CRITICAL → sin esta variable no hay investigación posible.
HIGH     → variable importante; su ausencia limita significativamente el diagnóstico.
MEDIUM   → variable útil; su ausencia reduce la calidad del diagnóstico.
LOW      → variable complementaria; su ausencia no bloquea la investigación.
"""

KnowledgeDomainType = Literal[
    "negocio",
    "matematica",
    "teoria_de_grafos",
    "estadistica",
    "optimizacion",
    "contabilidad",
    "finanzas",
    "logistica",
    "investigacion_operativa",
    "ciencia_de_datos",
    "economia",
    "derecho_tributario",
    "otro",
]
"""
Dominio de conocimiento de un tanque auxiliar.
"""

RoutePriority = Literal["P1", "P2", "P3"]
"""
Prioridad de una ruta investigativa.

P1 → máxima prioridad (sangría activa, evidencia disponible, alto impacto).
P2 → prioridad media.
P3 → prioridad baja (complementaria o de largo plazo).
"""


# ---------------------------------------------------------------------------
# KnowledgeDomain
# ---------------------------------------------------------------------------


class KnowledgeDomain(BaseModel):
    """
    Dominio de conocimiento activado para investigar un problema.

    Puede ser interno (catálogos SmartPyme) o externo (APIs, MCPs, fuentes académicas).
    """

    domain_id: str = Field(..., description="Identificador único del dominio.")
    domain_type: KnowledgeDomainType = Field(
        ..., description="Tipo de dominio de conocimiento."
    )
    name: str = Field(..., description="Nombre descriptivo del dominio.")
    is_external: bool = Field(
        default=False,
        description="Si el dominio requiere consulta a fuente externa.",
    )
    source_ref: Optional[str] = Field(
        default=None,
        description="Referencia a la fuente externa si aplica: URL, API, MCP tool.",
    )
    notes: Optional[str] = Field(default=None)


# ---------------------------------------------------------------------------
# KnowledgeToolCandidate
# ---------------------------------------------------------------------------


class KnowledgeToolCandidate(BaseModel):
    """
    Herramienta conceptual, matemática o algorítmica candidata para la investigación.

    Ejemplos: grafo dirigido, matriz de adyacencia, fórmula de margen, análisis de series.
    """

    tool_id: str = Field(..., description="Identificador único de la herramienta.")
    name: str = Field(..., description="Nombre de la herramienta.")
    knowledge_domain: KnowledgeDomain = Field(
        ..., description="Dominio de conocimiento al que pertenece la herramienta."
    )
    applies_to: list[str] = Field(
        ...,
        description="IDs de nodos o patologías a los que aplica esta herramienta.",
    )
    description: Optional[str] = Field(
        default=None,
        description="Descripción de cómo se aplica la herramienta al problema.",
    )
    confidence: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Confianza en la relevancia de esta herramienta para el caso.",
    )


# ---------------------------------------------------------------------------
# FormulaCandidate
# ---------------------------------------------------------------------------


class FormulaCandidate(BaseModel):
    """
    Fórmula o método investigativo candidato para una patología o variable.

    Ejemplos:
      diferencia_stock = stock_teorico - stock_actual
      capital_inmovilizado = stock_actual * costo_unitario
      margen_reposicion = precio_venta - costo_reposicion
    """

    formula_id: str = Field(..., description="Identificador único de la fórmula.")
    name: str = Field(..., description="Nombre descriptivo de la fórmula.")
    expression: str = Field(
        ...,
        description="Expresión de la fórmula como string legible.",
    )
    required_variable_ids: list[str] = Field(
        ...,
        description="IDs de las variables requeridas para calcular esta fórmula.",
    )
    output_variable_id: str = Field(
        ...,
        description="ID de la variable que produce esta fórmula.",
    )
    applies_to_pathology_ids: list[str] = Field(
        default_factory=list,
        description="IDs de patologías a las que aplica esta fórmula.",
    )
    notes: Optional[str] = Field(default=None)


# ---------------------------------------------------------------------------
# RequiredVariable
# ---------------------------------------------------------------------------


class RequiredVariable(BaseModel):
    """
    Variable requerida por una fórmula o patología para la investigación.

    Debe mapearse contra evidencia disponible (AvailableVariableMatch)
    o contra una brecha (EvidenceGap).
    """

    variable_id: str = Field(..., description="Identificador único de la variable requerida.")
    canonical_name: str = Field(
        ..., description="Nombre canónico de la variable: 'stock_actual', 'costo_unitario'."
    )
    required_by_formula_id: Optional[str] = Field(
        default=None,
        description="ID de la fórmula que requiere esta variable.",
    )
    required_by_pathology_id: Optional[str] = Field(
        default=None,
        description="ID de la patología que requiere esta variable.",
    )
    is_temporal: bool = Field(
        default=False,
        description="Si la variable requiere dimensión temporal para ser investigable.",
    )
    notes: Optional[str] = Field(default=None)


# ---------------------------------------------------------------------------
# AvailableVariableMatch
# ---------------------------------------------------------------------------


class AvailableVariableMatch(BaseModel):
    """
    Cruce entre una variable requerida y una variable disponible en el paquete normalizado.

    Confirma que la variable requerida tiene soporte de evidencia.
    """

    match_id: str = Field(..., description="Identificador único del match.")
    required_variable_id: str = Field(
        ..., description="ID de la RequiredVariable que fue satisfecha."
    )
    clean_variable_id: str = Field(
        ..., description="ID de la CleanVariable del NormalizedEvidencePackage."
    )
    evidence_ref_id: str = Field(
        ..., description="ID de la EvidenceReference que traza la variable a su fuente."
    )
    temporal_window_id: Optional[str] = Field(
        default=None,
        description="ID de la TemporalWindow asociada a la variable disponible.",
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confianza en que la variable disponible satisface la requerida.",
    )
    notes: Optional[str] = Field(default=None)


# ---------------------------------------------------------------------------
# EvidenceGap
# ---------------------------------------------------------------------------


class EvidenceGap(BaseModel):
    """
    Brecha de evidencia: variable requerida que no está disponible en el paquete normalizado.

    Cada brecha debe producir una tarea de evidencia o bloquear la ruta investigativa.
    """

    gap_id: str = Field(..., description="Identificador único de la brecha.")
    required_variable_id: str = Field(
        ..., description="ID de la RequiredVariable que no pudo satisfacerse."
    )
    variable_canonical_name: str = Field(
        ..., description="Nombre canónico de la variable faltante."
    )
    reason: str = Field(
        ..., description="Razón por la que la variable no está disponible."
    )
    impact: str = Field(
        ...,
        description="Impacto de esta brecha en la investigación: qué no se puede calcular.",
    )
    required_source: Optional[str] = Field(
        default=None,
        description="Fuente sugerida para obtener la variable faltante.",
    )
    suggested_task: Optional[str] = Field(
        default=None,
        description="Tarea sugerida para resolver la brecha.",
    )
    priority: GapPriority = Field(
        default="MEDIUM",
        description="Prioridad de la brecha: LOW, MEDIUM, HIGH o CRITICAL.",
    )


# ---------------------------------------------------------------------------
# InvestigationNode
# ---------------------------------------------------------------------------


class InvestigationNode(BaseModel):
    """
    Nodo del grafo investigativo.

    Puede representar síntomas, patologías, fórmulas, variables,
    evidencias, brechas o herramientas de conocimiento.
    """

    node_id: str = Field(..., description="Identificador único del nodo.")
    node_type: NodeType = Field(..., description="Tipo de nodo.")
    label: str = Field(
        ..., description="Etiqueta legible del nodo: nombre del síntoma, patología, etc."
    )
    description: Optional[str] = Field(
        default=None, description="Descripción adicional del nodo."
    )
    # Campos opcionales según tipo de nodo
    formula_candidate: Optional[FormulaCandidate] = Field(
        default=None,
        description="Fórmula asociada si node_type=FormulaNode.",
    )
    required_variable: Optional[RequiredVariable] = Field(
        default=None,
        description="Variable requerida si node_type=VariableNode.",
    )
    evidence_ref_id: Optional[str] = Field(
        default=None,
        description="ID de EvidenceReference si node_type=EvidenceNode.",
    )
    temporal_window_id: Optional[str] = Field(
        default=None,
        description="ID de TemporalWindow si el nodo requiere dimensión temporal.",
    )
    gap: Optional[EvidenceGap] = Field(
        default=None,
        description="Brecha de evidencia si node_type=GapNode.",
    )
    knowledge_tool: Optional[KnowledgeToolCandidate] = Field(
        default=None,
        description="Herramienta de conocimiento si node_type=KnowledgeToolNode.",
    )
    confidence: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Confianza en la relevancia de este nodo para el caso.",
    )
    roi_weight: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Peso de ROI para priorización de rutas. Rango [0, 1].",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Metadatos adicionales del nodo.",
    )


# ---------------------------------------------------------------------------
# InvestigationEdge
# ---------------------------------------------------------------------------


class InvestigationEdge(BaseModel):
    """
    Arista dirigida del grafo investigativo.

    Representa una relación semántica entre dos nodos.
    """

    edge_id: str = Field(..., description="Identificador único de la arista.")
    source_node_id: str = Field(..., description="ID del nodo de origen.")
    target_node_id: str = Field(..., description="ID del nodo de destino.")
    edge_type: EdgeType = Field(..., description="Tipo de relación entre los nodos.")
    weight: float = Field(
        default=1.0,
        ge=0.0,
        description="Peso de la arista para algoritmos de priorización.",
    )
    notes: Optional[str] = Field(default=None)


# ---------------------------------------------------------------------------
# InvestigationGraph
# ---------------------------------------------------------------------------


class InvestigationGraph(BaseModel):
    """
    Grafo investigativo completo.

    Representa la red de relaciones entre síntomas, patologías, fórmulas,
    variables, evidencias, brechas y herramientas de conocimiento.

    Es la unidad central de la Capa 2.
    """

    graph_id: str = Field(..., description="Identificador único del grafo.")
    cliente_id: str = Field(..., description="Tenant al que pertenece el grafo.")
    source_admission_case_id: Optional[str] = Field(
        default=None,
        description="ID del InitialCaseAdmission que originó este grafo.",
    )
    source_normalized_package_id: Optional[str] = Field(
        default=None,
        description="ID del NormalizedEvidencePackage que alimentó este grafo.",
    )
    nodes: list[InvestigationNode] = Field(
        default_factory=list,
        description="Nodos del grafo investigativo.",
    )
    edges: list[InvestigationEdge] = Field(
        default_factory=list,
        description="Aristas dirigidas del grafo investigativo.",
    )
    primary_pathology_node_id: Optional[str] = Field(
        default=None,
        description="ID del PathologyNode principal candidato.",
    )
    notes: Optional[str] = Field(default=None)


# ---------------------------------------------------------------------------
# InvestigationRoute
# ---------------------------------------------------------------------------


class InvestigationRoute(BaseModel):
    """
    Ruta investigativa priorizada dentro del grafo.

    Representa una secuencia de nodos que el sistema recomienda investigar
    en orden, según ROI, evidencia disponible y riesgo.
    """

    route_id: str = Field(..., description="Identificador único de la ruta.")
    graph_id: str = Field(..., description="ID del InvestigationGraph al que pertenece.")
    node_sequence: list[str] = Field(
        ...,
        description="Secuencia ordenada de node_ids que componen la ruta.",
    )
    priority: RoutePriority = Field(
        ..., description="Prioridad de la ruta: P1, P2 o P3."
    )
    rationale: str = Field(
        ...,
        description="Justificación de por qué esta ruta tiene esta prioridad.",
    )
    estimated_roi: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="ROI estimado de seguir esta ruta. Rango [0, 1].",
    )
    blocking_gaps: list[str] = Field(
        default_factory=list,
        description="IDs de EvidenceGap que bloquean o limitan esta ruta.",
    )
    notes: Optional[str] = Field(default=None)


# ---------------------------------------------------------------------------
# InvestigationPlan
# ---------------------------------------------------------------------------


class InvestigationPlan(BaseModel):
    """
    Plan investigativo completo: grafo + rutas priorizadas.

    Consolida el grafo investigativo y las rutas recomendadas para
    presentar al dueño antes de crear el OperationalCase.
    """

    plan_id: str = Field(..., description="Identificador único del plan.")
    cliente_id: str = Field(..., description="Tenant al que pertenece el plan.")
    graph: InvestigationGraph = Field(
        ..., description="Grafo investigativo completo."
    )
    routes: list[InvestigationRoute] = Field(
        default_factory=list,
        description="Rutas investigativas priorizadas.",
    )
    recommended_route_id: Optional[str] = Field(
        default=None,
        description="ID de la ruta recomendada como punto de partida.",
    )
    evidence_gaps: list[EvidenceGap] = Field(
        default_factory=list,
        description="Brechas de evidencia detectadas en el plan.",
    )
    knowledge_tools: list[KnowledgeToolCandidate] = Field(
        default_factory=list,
        description="Herramientas de conocimiento activadas para este plan.",
    )
    next_step: str = Field(
        ...,
        description="Próximo paso sugerido para el dueño o el sistema.",
    )
    notes: Optional[str] = Field(default=None)


# ---------------------------------------------------------------------------
# OperationalCaseCandidate
# ---------------------------------------------------------------------------


class OperationalCaseCandidate(BaseModel):
    """
    Output de la Capa 2: candidato de caso operativo.

    NO es un OperationalCase.
    NO es un diagnóstico.

    Es la propuesta investigativa que el sistema presenta al dueño
    antes de iniciar la investigación formal.

    Solo se convierte en OperationalCase cuando:
      - hay evidencia mínima suficiente;
      - el dueño valida el alcance;
      - las variables críticas están disponibles o sus tareas aceptadas;
      - la ruta prioritaria está aprobada.
    """

    candidate_id: str = Field(..., description="Identificador único del candidato.")
    cliente_id: str = Field(..., description="Tenant al que pertenece el candidato.")
    source_admission_case_id: Optional[str] = Field(
        default=None,
        description="ID del InitialCaseAdmission de origen.",
    )
    source_normalized_package_id: Optional[str] = Field(
        default=None,
        description="ID del NormalizedEvidencePackage de origen.",
    )
    primary_pathology: str = Field(
        ...,
        description="ID o nombre de la patología principal candidata.",
    )
    hypothesis: str = Field(
        ...,
        description=(
            "Hipótesis investigable formulada por Capa 02. "
            "No afirma: investiga. "
            "Ejemplo: 'Investigar si existe pérdida de margen por desalineación "
            "entre costos reales y precios de venta durante el período mayo 2026.'"
        ),
    )

    @field_validator("hypothesis")
    @classmethod
    def hypothesis_not_empty(cls, v: str) -> str:
        """hypothesis no puede estar vacía."""
        if not v or not v.strip():
            raise ValueError("hypothesis no puede estar vacía.")
        return v
    related_pathologies: list[str] = Field(
        default_factory=list,
        description="IDs o nombres de patologías relacionadas.",
    )
    activated_formulas: list[FormulaCandidate] = Field(
        default_factory=list,
        description="Fórmulas activadas para investigar la patología principal.",
    )
    required_variables: list[RequiredVariable] = Field(
        default_factory=list,
        description="Variables requeridas para la investigación.",
    )
    available_variables: list[AvailableVariableMatch] = Field(
        default_factory=list,
        description="Variables disponibles que satisfacen variables requeridas.",
    )
    evidence_gaps: list[EvidenceGap] = Field(
        default_factory=list,
        description="Brechas de evidencia detectadas.",
    )
    knowledge_tools: list[KnowledgeToolCandidate] = Field(
        default_factory=list,
        description="Herramientas de conocimiento activadas.",
    )
    investigation_graph: Optional[InvestigationGraph] = Field(
        default=None,
        description="Grafo investigativo completo.",
    )
    recommended_route: Optional[InvestigationRoute] = Field(
        default=None,
        description="Ruta investigativa recomendada.",
    )
    next_step: str = Field(
        ...,
        description="Próximo paso sugerido para el dueño o el sistema.",
    )
    status: CandidateStatus = Field(
        ...,
        description="Estado del candidato.",
    )
    notes: Optional[str] = Field(default=None)
