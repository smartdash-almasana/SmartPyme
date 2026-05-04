"""
Tests — Contratos Pydantic Capa 2: Activación de Conocimiento e Investigación
TS_020_001_CONTRATOS_ACTIVACION_INVESTIGATIVA

Valida los contratos definidos en app/contracts/investigation_contract.py.

Cobertura requerida:
  1.  Crear grafo mínimo con PathologyNode y FormulaNode vinculados.
  2.  RequiredVariable asociada a EvidenceNode o GapNode según disponibilidad.
  3.  InvestigationGraph contiene nodos y edges correctamente tipados.
  4.  InvestigationRoute prioriza PathologyNode según ROI (dummy test).
  5.  OperationalCaseCandidate tiene candidate_id, cliente_id, primary_pathology y next_step.
  6.  InvestigationPlan puede almacenar un nodo, un edge y una ruta simple.
  7.  EvidenceGap se genera correctamente para variable faltante.
  8.  KnowledgeToolCandidate contiene tool_id, knowledge_domain y applies_to.
  9.  InvestigationGraph puede contener múltiples nodos interconectados.
  10. TemporalWindow y evidencia referenciada presentes en nodos que requieren variable temporal.
"""

import pytest
from pydantic import ValidationError

from app.contracts.investigation_contract import (
    AvailableVariableMatch,
    EvidenceGap,
    FormulaCandidate,
    InvestigationEdge,
    InvestigationGraph,
    InvestigationNode,
    InvestigationPlan,
    InvestigationRoute,
    KnowledgeDomain,
    KnowledgeToolCandidate,
    OperationalCaseCandidate,
    RequiredVariable,
)


# ---------------------------------------------------------------------------
# Helpers de construcción
# ---------------------------------------------------------------------------


def _domain_grafos() -> KnowledgeDomain:
    return KnowledgeDomain(
        domain_id="dom_grafos",
        domain_type="teoria_de_grafos",
        name="Teoría de Grafos",
    )


def _domain_finanzas() -> KnowledgeDomain:
    return KnowledgeDomain(
        domain_id="dom_finanzas",
        domain_type="finanzas",
        name="Finanzas operativas",
    )


def _formula_capital_inmovilizado() -> FormulaCandidate:
    return FormulaCandidate(
        formula_id="formula_capital_inmovilizado",
        name="Capital inmovilizado",
        expression="capital_inmovilizado = stock_actual * costo_unitario",
        required_variable_ids=["var_stock_actual", "var_costo_unitario"],
        output_variable_id="var_capital_inmovilizado",
        applies_to_pathology_ids=["path_inventario_no_confiable"],
    )


def _node_pathology(node_id: str = "node_path_001") -> InvestigationNode:
    return InvestigationNode(
        node_id=node_id,
        node_type="PathologyNode",
        label="inventario_no_confiable",
        description="Stock declarado sin conteo físico confirmado.",
        confidence=0.85,
        roi_weight=0.9,
    )


def _node_formula(node_id: str = "node_form_001") -> InvestigationNode:
    return InvestigationNode(
        node_id=node_id,
        node_type="FormulaNode",
        label="capital_inmovilizado",
        formula_candidate=_formula_capital_inmovilizado(),
        confidence=0.80,
    )


def _node_variable(
    node_id: str = "node_var_001",
    var_id: str = "var_stock_actual",
    is_temporal: bool = False,
) -> InvestigationNode:
    return InvestigationNode(
        node_id=node_id,
        node_type="VariableNode",
        label=var_id,
        required_variable=RequiredVariable(
            variable_id=var_id,
            canonical_name=var_id,
            required_by_formula_id="formula_capital_inmovilizado",
            is_temporal=is_temporal,
        ),
        confidence=0.82,
    )


def _node_evidence(
    node_id: str = "node_ev_001",
    evidence_ref_id: str = "ref_001",
    temporal_window_id: str = "tw_001",
) -> InvestigationNode:
    return InvestigationNode(
        node_id=node_id,
        node_type="EvidenceNode",
        label="excel_paulita.stock",
        evidence_ref_id=evidence_ref_id,
        temporal_window_id=temporal_window_id,
        confidence=0.82,
    )


def _node_gap(node_id: str = "node_gap_001") -> InvestigationNode:
    return InvestigationNode(
        node_id=node_id,
        node_type="GapNode",
        label="costo_unitario_faltante",
        gap=EvidenceGap(
            gap_id="gap_costo_unitario",
            required_variable_id="var_costo_unitario",
            variable_canonical_name="costo_unitario",
            reason="No se encontró columna de costo unitario en el documento.",
            impact="No se puede calcular capital_inmovilizado.",
            suggested_task="Pedir lista de costos al dueño o contador.",
            priority="HIGH",
        ),
        confidence=0.0,
    )


def _edge(
    edge_id: str,
    source: str,
    target: str,
    edge_type: str = "REQUIRES",
) -> InvestigationEdge:
    return InvestigationEdge(
        edge_id=edge_id,
        source_node_id=source,
        target_node_id=target,
        edge_type=edge_type,  # type: ignore[arg-type]
    )


def _minimal_graph(graph_id: str = "graph_001") -> InvestigationGraph:
    path_node = _node_pathology()
    form_node = _node_formula()
    edge = _edge("edge_001", path_node.node_id, form_node.node_id, "REQUIRES")
    return InvestigationGraph(
        graph_id=graph_id,
        cliente_id="cliente_perales",
        nodes=[path_node, form_node],
        edges=[edge],
        primary_pathology_node_id=path_node.node_id,
    )


# ---------------------------------------------------------------------------
# Test 1: Grafo mínimo con PathologyNode y FormulaNode vinculados
# ---------------------------------------------------------------------------


def test_minimal_graph_with_pathology_and_formula_nodes():
    """Grafo mínimo con PathologyNode y FormulaNode vinculados debe construirse sin errores."""
    graph = _minimal_graph()

    assert graph.graph_id == "graph_001"
    assert len(graph.nodes) == 2
    assert len(graph.edges) == 1

    node_types = {n.node_type for n in graph.nodes}
    assert "PathologyNode" in node_types
    assert "FormulaNode" in node_types

    edge = graph.edges[0]
    assert edge.source_node_id == "node_path_001"
    assert edge.target_node_id == "node_form_001"
    assert edge.edge_type == "REQUIRES"


# ---------------------------------------------------------------------------
# Test 2: RequiredVariable asociada a EvidenceNode o GapNode
# ---------------------------------------------------------------------------


def test_required_variable_associated_with_evidence_node():
    """VariableNode con evidencia disponible debe tener EvidenceNode vinculado."""
    var_node = _node_variable("node_var_stock", "var_stock_actual")
    ev_node = _node_evidence("node_ev_stock", "ref_stock_001", "tw_001")
    edge = _edge("edge_var_ev", var_node.node_id, ev_node.node_id, "SUPPORTED_BY")

    graph = InvestigationGraph(
        graph_id="graph_var_ev",
        cliente_id="cliente_x",
        nodes=[var_node, ev_node],
        edges=[edge],
    )

    # El VariableNode tiene RequiredVariable
    var_nodes = [n for n in graph.nodes if n.node_type == "VariableNode"]
    assert len(var_nodes) == 1
    assert var_nodes[0].required_variable is not None
    assert var_nodes[0].required_variable.variable_id == "var_stock_actual"

    # El edge SUPPORTED_BY conecta variable con evidencia
    supported_edges = [e for e in graph.edges if e.edge_type == "SUPPORTED_BY"]
    assert len(supported_edges) == 1


def test_required_variable_associated_with_gap_node():
    """VariableNode sin evidencia debe tener GapNode vinculado."""
    var_node = _node_variable("node_var_costo", "var_costo_unitario")
    gap_node = _node_gap("node_gap_costo")
    edge = _edge("edge_var_gap", var_node.node_id, gap_node.node_id, "MISSING")

    graph = InvestigationGraph(
        graph_id="graph_var_gap",
        cliente_id="cliente_x",
        nodes=[var_node, gap_node],
        edges=[edge],
    )

    gap_nodes = [n for n in graph.nodes if n.node_type == "GapNode"]
    assert len(gap_nodes) == 1
    assert gap_nodes[0].gap is not None
    assert gap_nodes[0].gap.priority == "HIGH"

    missing_edges = [e for e in graph.edges if e.edge_type == "MISSING"]
    assert len(missing_edges) == 1


# ---------------------------------------------------------------------------
# Test 3: InvestigationGraph con nodos y edges correctamente tipados
# ---------------------------------------------------------------------------


def test_investigation_graph_nodes_and_edges_typed():
    """InvestigationGraph debe aceptar todos los tipos de nodos y edges."""
    nodes = [
        InvestigationNode(node_id="n_sym", node_type="SymptomNode", label="stock_desordenado"),
        InvestigationNode(node_id="n_path", node_type="PathologyNode", label="inventario_no_confiable"),
        InvestigationNode(node_id="n_form", node_type="FormulaNode", label="capital_inmovilizado"),
        InvestigationNode(node_id="n_var", node_type="VariableNode", label="stock_actual"),
        InvestigationNode(node_id="n_ev", node_type="EvidenceNode", label="excel_paulita.stock"),
        InvestigationNode(node_id="n_gap", node_type="GapNode", label="costo_unitario_faltante"),
        InvestigationNode(node_id="n_tool", node_type="KnowledgeToolNode", label="grafo_dirigido"),
    ]
    edges = [
        _edge("e1", "n_sym",  "n_path", "TRIGGERS"),
        _edge("e2", "n_path", "n_form", "REQUIRES"),
        _edge("e3", "n_form", "n_var",  "REQUIRES"),
        _edge("e4", "n_var",  "n_ev",   "SUPPORTED_BY"),
        _edge("e5", "n_var",  "n_gap",  "MISSING"),
        _edge("e6", "n_path", "n_tool", "USES_TOOL"),
    ]

    graph = InvestigationGraph(
        graph_id="graph_full",
        cliente_id="cliente_x",
        nodes=nodes,
        edges=edges,
    )

    assert len(graph.nodes) == 7
    assert len(graph.edges) == 6

    node_types = {n.node_type for n in graph.nodes}
    assert node_types == {
        "SymptomNode", "PathologyNode", "FormulaNode",
        "VariableNode", "EvidenceNode", "GapNode", "KnowledgeToolNode"
    }

    edge_types = {e.edge_type for e in graph.edges}
    assert "TRIGGERS" in edge_types
    assert "SUPPORTED_BY" in edge_types
    assert "MISSING" in edge_types
    assert "USES_TOOL" in edge_types


# ---------------------------------------------------------------------------
# Test 4: InvestigationRoute prioriza PathologyNode según ROI (dummy)
# ---------------------------------------------------------------------------


def test_investigation_route_prioritizes_by_roi():
    """InvestigationRoute con P1 y roi_weight alto debe construirse correctamente."""
    graph = _minimal_graph("graph_roi")

    route = InvestigationRoute(
        route_id="route_001",
        graph_id="graph_roi",
        node_sequence=["node_path_001", "node_form_001"],
        priority="P1",
        rationale="Patología con mayor ROI y evidencia disponible.",
        estimated_roi=0.9,
    )

    assert route.priority == "P1"
    assert route.estimated_roi == 0.9
    assert "node_path_001" in route.node_sequence

    # El PathologyNode tiene roi_weight alto
    path_node = next(n for n in graph.nodes if n.node_type == "PathologyNode")
    assert path_node.roi_weight >= 0.8


# ---------------------------------------------------------------------------
# Test 5: OperationalCaseCandidate tiene campos mínimos requeridos
# ---------------------------------------------------------------------------


def test_operational_case_candidate_required_fields():
    """OperationalCaseCandidate debe tener candidate_id, cliente_id, primary_pathology y next_step."""
    candidate = OperationalCaseCandidate(
        candidate_id="cand_001",
        cliente_id="cliente_perales",
        primary_pathology="inventario_no_confiable",
        next_step="Confirmar stock físico con Paulita antes de calcular capital inmovilizado.",
        status="PARTIAL_EVIDENCE",
    )

    assert candidate.candidate_id == "cand_001"
    assert candidate.cliente_id == "cliente_perales"
    assert candidate.primary_pathology == "inventario_no_confiable"
    assert candidate.next_step != ""


def test_operational_case_candidate_is_not_operational_case():
    """OperationalCaseCandidate no debe tener atributos de OperationalCase."""
    candidate = OperationalCaseCandidate(
        candidate_id="cand_002",
        cliente_id="cliente_x",
        primary_pathology="caja_fragmentada",
        next_step="Pedir reporte del contador.",
        status="BLOCKED_MISSING_VARIABLES",
    )

    assert not hasattr(candidate, "hypothesis")
    assert not hasattr(candidate, "job_id")
    assert not hasattr(candidate, "diagnosis_status")
    assert not hasattr(candidate, "skill_id")


# ---------------------------------------------------------------------------
# Test 6: InvestigationPlan almacena nodo, edge y ruta simple
# ---------------------------------------------------------------------------


def test_investigation_plan_stores_node_edge_and_route():
    """InvestigationPlan debe poder almacenar un nodo, un edge y una ruta simple."""
    graph = _minimal_graph("graph_plan")
    route = InvestigationRoute(
        route_id="route_plan_001",
        graph_id="graph_plan",
        node_sequence=["node_path_001", "node_form_001"],
        priority="P1",
        rationale="Ruta principal por ROI.",
        estimated_roi=0.85,
    )

    plan = InvestigationPlan(
        plan_id="plan_001",
        cliente_id="cliente_perales",
        graph=graph,
        routes=[route],
        recommended_route_id="route_plan_001",
        next_step="Validar ruta con el dueño antes de investigar.",
    )

    assert plan.plan_id == "plan_001"
    assert len(plan.graph.nodes) == 2
    assert len(plan.graph.edges) == 1
    assert len(plan.routes) == 1
    assert plan.recommended_route_id == "route_plan_001"
    assert plan.next_step != ""


# ---------------------------------------------------------------------------
# Test 7: EvidenceGap se genera correctamente para variable faltante
# ---------------------------------------------------------------------------


def test_evidence_gap_for_missing_variable():
    """EvidenceGap debe construirse con todos los campos requeridos."""
    gap = EvidenceGap(
        gap_id="gap_costo_reposicion",
        required_variable_id="var_costo_reposicion",
        variable_canonical_name="costo_reposicion",
        reason="No se encontró columna de costo de reposición en el Excel de Paulita.",
        impact="No se puede calcular margen_reposicion = precio_venta - costo_reposicion.",
        required_source="Lista de costos del proveedor o factura de compra.",
        suggested_task="Pedir al dueño la lista de costos actualizada.",
        priority="CRITICAL",
    )

    assert gap.gap_id == "gap_costo_reposicion"
    assert gap.required_variable_id == "var_costo_reposicion"
    assert gap.priority == "CRITICAL"
    assert gap.impact != ""
    assert gap.suggested_task is not None


def test_evidence_gap_default_priority_is_medium():
    """EvidenceGap sin priority explícita debe tener MEDIUM por defecto."""
    gap = EvidenceGap(
        gap_id="gap_default",
        required_variable_id="var_x",
        variable_canonical_name="variable_x",
        reason="Variable no disponible.",
        impact="Impacto menor.",
    )
    assert gap.priority == "MEDIUM"


# ---------------------------------------------------------------------------
# Test 8: KnowledgeToolCandidate contiene tool_id, knowledge_domain y applies_to
# ---------------------------------------------------------------------------


def test_knowledge_tool_candidate_required_fields():
    """KnowledgeToolCandidate debe tener tool_id, knowledge_domain y applies_to."""
    tool = KnowledgeToolCandidate(
        tool_id="tool_grafo_dirigido",
        name="Grafo dirigido de dependencias",
        knowledge_domain=_domain_grafos(),
        applies_to=["node_path_001", "node_form_001"],
        description="Modela propagación de inventario hacia precios, margen y flujo de caja.",
        confidence=0.85,
    )

    assert tool.tool_id == "tool_grafo_dirigido"
    assert tool.knowledge_domain.domain_type == "teoria_de_grafos"
    assert len(tool.applies_to) == 2
    assert tool.confidence == 0.85


def test_knowledge_tool_candidate_confidence_bounds():
    """KnowledgeToolCandidate.confidence rechaza valores fuera de [0, 1]."""
    with pytest.raises(ValidationError):
        KnowledgeToolCandidate(
            tool_id="tool_bad",
            name="Tool malo",
            knowledge_domain=_domain_finanzas(),
            applies_to=["node_x"],
            confidence=1.5,
        )


# ---------------------------------------------------------------------------
# Test 9: InvestigationGraph con múltiples nodos interconectados
# ---------------------------------------------------------------------------


def test_investigation_graph_multiple_interconnected_nodes():
    """InvestigationGraph debe soportar múltiples nodos con relaciones en cadena."""
    # Cadena: stock_desordenado → inventario_no_confiable → capital_inmovilizado → margen_invisible
    nodes = [
        InvestigationNode(node_id="n1", node_type="SymptomNode",   label="stock_desordenado",       roi_weight=0.5),
        InvestigationNode(node_id="n2", node_type="PathologyNode", label="inventario_no_confiable",  roi_weight=0.9),
        InvestigationNode(node_id="n3", node_type="PathologyNode", label="capital_inmovilizado",     roi_weight=0.85),
        InvestigationNode(node_id="n4", node_type="PathologyNode", label="margen_invisible",         roi_weight=0.8),
        InvestigationNode(node_id="n5", node_type="FormulaNode",   label="formula_capital",          roi_weight=0.7),
    ]
    edges = [
        _edge("e1", "n1", "n2", "TRIGGERS"),
        _edge("e2", "n2", "n3", "IMPACTS"),
        _edge("e3", "n3", "n4", "IMPACTS"),
        _edge("e4", "n2", "n5", "REQUIRES"),
    ]

    graph = InvestigationGraph(
        graph_id="graph_chain",
        cliente_id="cliente_perales",
        nodes=nodes,
        edges=edges,
        primary_pathology_node_id="n2",
    )

    assert len(graph.nodes) == 5
    assert len(graph.edges) == 4
    assert graph.primary_pathology_node_id == "n2"

    # Verificar cadena de impacto
    impact_edges = [e for e in graph.edges if e.edge_type == "IMPACTS"]
    assert len(impact_edges) == 2

    # Verificar que el nodo primario tiene el mayor roi_weight
    primary = next(n for n in graph.nodes if n.node_id == "n2")
    assert primary.roi_weight == max(n.roi_weight for n in graph.nodes)


# ---------------------------------------------------------------------------
# Test 10: TemporalWindow y evidencia referenciada en nodos con variable temporal
# ---------------------------------------------------------------------------


def test_temporal_variable_node_has_temporal_window_and_evidence_ref():
    """
    Un VariableNode con is_temporal=True debe tener temporal_window_id y evidence_ref_id
    en el EvidenceNode vinculado.
    """
    # VariableNode temporal
    var_node = _node_variable("node_var_ventas", "var_ventas_periodo", is_temporal=True)
    assert var_node.required_variable is not None
    assert var_node.required_variable.is_temporal is True

    # EvidenceNode con temporal_window_id y evidence_ref_id
    ev_node = _node_evidence(
        node_id="node_ev_ventas",
        evidence_ref_id="ref_ventas_001",
        temporal_window_id="tw_ventas_abril",
    )
    assert ev_node.evidence_ref_id == "ref_ventas_001"
    assert ev_node.temporal_window_id == "tw_ventas_abril"

    # Edge SUPPORTED_BY conecta variable temporal con evidencia
    edge = _edge("edge_temporal", var_node.node_id, ev_node.node_id, "SUPPORTED_BY")

    graph = InvestigationGraph(
        graph_id="graph_temporal",
        cliente_id="cliente_x",
        nodes=[var_node, ev_node],
        edges=[edge],
    )

    # Verificar que el grafo tiene el nodo temporal con su evidencia
    temporal_vars = [
        n for n in graph.nodes
        if n.node_type == "VariableNode"
        and n.required_variable is not None
        and n.required_variable.is_temporal
    ]
    assert len(temporal_vars) == 1

    evidence_nodes = [n for n in graph.nodes if n.node_type == "EvidenceNode"]
    assert len(evidence_nodes) == 1
    assert evidence_nodes[0].temporal_window_id is not None
    assert evidence_nodes[0].evidence_ref_id is not None
