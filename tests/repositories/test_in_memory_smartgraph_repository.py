from __future__ import annotations

from uuid import UUID, uuid4

import pytest

from app.repositories.in_memory_smartgraph_repository import InMemorySmartGraphRepository


ZERO_UUID = UUID("00000000-0000-0000-0000-000000000000")


@pytest.fixture
def tenant_id() -> UUID:
    return uuid4()


@pytest.fixture
def other_tenant_id() -> UUID:
    return uuid4()


@pytest.fixture
def repo() -> InMemorySmartGraphRepository:
    return InMemorySmartGraphRepository()


def create_node(
    repo: InMemorySmartGraphRepository,
    tenant_id: UUID,
    *,
    node_type: str = "PRODUCTO",
    canonical_key: str = "producto_a",
    label: str = "Producto A",
    confidence: float | None = None,
) -> dict:
    return repo.create_node(
        tenant_id=tenant_id,
        node_type=node_type,  # type: ignore[arg-type]
        canonical_key=canonical_key,
        label=label,
        confidence=confidence,
    )


def test_create_and_get_node(repo: InMemorySmartGraphRepository, tenant_id: UUID) -> None:
    node = create_node(repo, tenant_id)

    assert node["tenant_id"] == tenant_id
    assert node["node_type"] == "PRODUCTO"
    assert node["canonical_key"] == "producto_a"
    assert node["label"] == "Producto A"
    assert node["status"] == "ACTIVE"

    fetched = repo.get_node(tenant_id=tenant_id, node_id=node["id"])
    assert fetched == node


def test_get_node_fail_closed_by_tenant(
    repo: InMemorySmartGraphRepository,
    tenant_id: UUID,
    other_tenant_id: UUID,
) -> None:
    node = create_node(repo, tenant_id)

    assert repo.get_node(tenant_id=other_tenant_id, node_id=node["id"]) is None


def test_create_node_rejects_duplicate_canonical_key_per_tenant(
    repo: InMemorySmartGraphRepository,
    tenant_id: UUID,
) -> None:
    create_node(repo, tenant_id)

    with pytest.raises(ValueError, match="already exists"):
        create_node(repo, tenant_id)


def test_same_canonical_key_allowed_across_tenants(
    repo: InMemorySmartGraphRepository,
    tenant_id: UUID,
    other_tenant_id: UUID,
) -> None:
    node_a = create_node(repo, tenant_id)
    node_b = create_node(repo, other_tenant_id)

    assert node_a["tenant_id"] != node_b["tenant_id"]
    assert node_a["canonical_key"] == node_b["canonical_key"]


def test_list_nodes_filters_by_type_and_status(
    repo: InMemorySmartGraphRepository,
    tenant_id: UUID,
) -> None:
    product = create_node(repo, tenant_id, node_type="PRODUCTO", canonical_key="p1")
    create_node(repo, tenant_id, node_type="PROVEEDOR", canonical_key="prov1")

    nodes = repo.list_nodes(tenant_id=tenant_id, node_type="PRODUCTO")

    assert [node["id"] for node in nodes] == [product["id"]]


def test_create_edge_between_nodes(repo: InMemorySmartGraphRepository, tenant_id: UUID) -> None:
    symptom = create_node(
        repo,
        tenant_id,
        node_type="SINTOMA",
        canonical_key="vendo_mucho_no_queda_plata",
        label="Vendo mucho pero no queda plata",
    )
    pathology = create_node(
        repo,
        tenant_id,
        node_type="PATOLOGIA",
        canonical_key="margen_erosionado",
        label="Margen erosionado",
    )

    edge = repo.create_edge(
        tenant_id=tenant_id,
        from_node_id=symptom["id"],
        to_node_id=pathology["id"],
        edge_type="INDICATES",
        claim_type="HYPOTHESIS",
        confidence=0.62,
    )

    assert edge["tenant_id"] == tenant_id
    assert edge["from_node_id"] == symptom["id"]
    assert edge["to_node_id"] == pathology["id"]
    assert edge["edge_type"] == "INDICATES"
    assert edge["claim_type"] == "HYPOTHESIS"
    assert edge["confidence"] == 0.62


def test_create_edge_rejects_cross_tenant_nodes(
    repo: InMemorySmartGraphRepository,
    tenant_id: UUID,
    other_tenant_id: UUID,
) -> None:
    from_node = create_node(repo, tenant_id, canonical_key="p1")
    to_node = create_node(repo, other_tenant_id, canonical_key="p2")

    with pytest.raises(ValueError, match="to_node_id does not exist for tenant"):
        repo.create_edge(
            tenant_id=tenant_id,
            from_node_id=from_node["id"],
            to_node_id=to_node["id"],
            edge_type="DEPENDS_ON",
            claim_type="EXTRACTED",
        )


def test_create_edge_rejects_self_edge(
    repo: InMemorySmartGraphRepository,
    tenant_id: UUID,
) -> None:
    node = create_node(repo, tenant_id)

    with pytest.raises(ValueError, match="self-edges"):
        repo.create_edge(
            tenant_id=tenant_id,
            from_node_id=node["id"],
            to_node_id=node["id"],
            edge_type="DEPENDS_ON",
            claim_type="EXTRACTED",
        )


def test_list_edges_for_node_direction_filters(
    repo: InMemorySmartGraphRepository,
    tenant_id: UUID,
) -> None:
    product = create_node(repo, tenant_id, node_type="PRODUCTO", canonical_key="p1")
    supplier = create_node(repo, tenant_id, node_type="PROVEEDOR", canonical_key="s1")
    edge = repo.create_edge(
        tenant_id=tenant_id,
        from_node_id=product["id"],
        to_node_id=supplier["id"],
        edge_type="DEPENDS_ON",
        claim_type="EXTRACTED",
    )

    outgoing = repo.list_edges_for_node(tenant_id=tenant_id, node_id=product["id"], direction="OUT")
    incoming = repo.list_edges_for_node(tenant_id=tenant_id, node_id=product["id"], direction="IN")

    assert [item["id"] for item in outgoing] == [edge["id"]]
    assert incoming == []


def test_add_alias_and_find_nodes_by_alias(
    repo: InMemorySmartGraphRepository,
    tenant_id: UUID,
) -> None:
    node = create_node(
        repo,
        tenant_id,
        node_type="PRODUCTO",
        canonical_key="product_stock",
        label="Stock de productos",
    )

    alias = repo.add_alias(
        tenant_id=tenant_id,
        node_id=node["id"],
        alias="mercadería",
        alias_normalized="mercaderia",
        language="es",
        confidence=0.9,
    )

    assert alias["node_id"] == node["id"]
    assert alias["alias_normalized"] == "mercaderia"

    matches = repo.find_nodes_by_alias(tenant_id=tenant_id, alias_normalized="mercaderia")
    assert [match["id"] for match in matches] == [node["id"]]


def test_add_alias_rejects_unknown_node(
    repo: InMemorySmartGraphRepository,
    tenant_id: UUID,
) -> None:
    with pytest.raises(ValueError, match="node_id does not exist"):
        repo.add_alias(
            tenant_id=tenant_id,
            node_id=uuid4(),
            alias="stock",
            alias_normalized="stock",
        )


def test_create_claim_candidate(repo: InMemorySmartGraphRepository, tenant_id: UUID) -> None:
    node = create_node(repo, tenant_id, node_type="PATOLOGIA", canonical_key="margen_erosionado")

    claim = repo.create_claim(
        tenant_id=tenant_id,
        claim_type="HYPOTHESIS",
        claim_status="CANDIDATE",
        statement="Puede existir margen erosionado.",
        subject_node_id=node["id"],
        confidence=0.6,
        requires_human_review=True,
    )

    assert claim["claim_type"] == "HYPOTHESIS"
    assert claim["claim_status"] == "CANDIDATE"
    assert claim["requires_human_review"] is True


def test_hypothesis_claim_cannot_be_supported_without_evidence_or_review(
    repo: InMemorySmartGraphRepository,
    tenant_id: UUID,
) -> None:
    with pytest.raises(ValueError, match="cannot become SUPPORTED"):
        repo.create_claim(
            tenant_id=tenant_id,
            claim_type="HYPOTHESIS",
            claim_status="SUPPORTED",
            statement="Puede existir margen erosionado.",
            confidence=0.6,
        )


def test_hypothesis_claim_can_be_supported_with_evidence(
    repo: InMemorySmartGraphRepository,
    tenant_id: UUID,
) -> None:
    claim = repo.create_claim(
        tenant_id=tenant_id,
        claim_type="HYPOTHESIS",
        claim_status="SUPPORTED",
        statement="Puede existir margen erosionado.",
        confidence=0.6,
        evidence_ids=[uuid4()],
    )

    assert claim["claim_status"] == "SUPPORTED"


def test_claim_requiring_human_review_cannot_be_supported_without_review(
    repo: InMemorySmartGraphRepository,
    tenant_id: UUID,
) -> None:
    claim = repo.create_claim(
        tenant_id=tenant_id,
        claim_type="HYPOTHESIS",
        claim_status="CANDIDATE",
        statement="Puede existir dependencia crítica de proveedor.",
        requires_human_review=True,
        evidence_ids=[uuid4()],
    )

    with pytest.raises(ValueError, match="requires human review"):
        repo.update_claim_status(
            tenant_id=tenant_id,
            claim_id=claim["id"],
            claim_status="SUPPORTED",
        )


def test_claim_requiring_human_review_can_be_supported_with_review(
    repo: InMemorySmartGraphRepository,
    tenant_id: UUID,
) -> None:
    claim = repo.create_claim(
        tenant_id=tenant_id,
        claim_type="HYPOTHESIS",
        claim_status="CANDIDATE",
        statement="Puede existir dependencia crítica de proveedor.",
        requires_human_review=True,
        evidence_ids=[uuid4()],
    )

    updated = repo.update_claim_status(
        tenant_id=tenant_id,
        claim_id=claim["id"],
        claim_status="SUPPORTED",
        reviewed_by="owner",
        review_decision="approved",
    )

    assert updated["claim_status"] == "SUPPORTED"
    assert updated["reviewed_by"] == "owner"
    assert updated["review_decision"] == "approved"
    assert updated["reviewed_at"] is not None


def test_list_claims_filters(
    repo: InMemorySmartGraphRepository,
    tenant_id: UUID,
) -> None:
    repo.create_claim(
        tenant_id=tenant_id,
        claim_type="HYPOTHESIS",
        claim_status="CANDIDATE",
        statement="Hipótesis 1",
        requires_human_review=True,
    )
    repo.create_claim(
        tenant_id=tenant_id,
        claim_type="EXTRACTED",
        claim_status="ACTIVE",
        statement="Dato extraído",
    )

    claims = repo.list_claims(
        tenant_id=tenant_id,
        claim_type="HYPOTHESIS",
        requires_human_review=True,
    )

    assert len(claims) == 1
    assert claims[0]["statement"] == "Hipótesis 1"


def test_activation_subgraph_respects_depth(repo: InMemorySmartGraphRepository, tenant_id: UUID) -> None:
    symptom = create_node(repo, tenant_id, node_type="SINTOMA", canonical_key="sintoma")
    pathology = create_node(repo, tenant_id, node_type="PATOLOGIA", canonical_key="patologia")
    formula = create_node(repo, tenant_id, node_type="FORMULA", canonical_key="formula")

    repo.create_edge(
        tenant_id=tenant_id,
        from_node_id=symptom["id"],
        to_node_id=pathology["id"],
        edge_type="INDICATES",
        claim_type="HYPOTHESIS",
    )
    repo.create_edge(
        tenant_id=tenant_id,
        from_node_id=pathology["id"],
        to_node_id=formula["id"],
        edge_type="REQUIRES_VARIABLE",
        claim_type="VALIDATED",
    )

    subgraph_depth_1 = repo.get_activation_subgraph(
        tenant_id=tenant_id,
        seed_node_ids=[symptom["id"]],
        depth=1,
    )
    subgraph_depth_2 = repo.get_activation_subgraph(
        tenant_id=tenant_id,
        seed_node_ids=[symptom["id"]],
        depth=2,
    )

    assert {node["id"] for node in subgraph_depth_1["nodes"]} == {
        symptom["id"],
        pathology["id"],
    }
    assert {node["id"] for node in subgraph_depth_2["nodes"]} == {
        symptom["id"],
        pathology["id"],
        formula["id"],
    }


def test_activation_subgraph_filters_edge_and_claim_types(
    repo: InMemorySmartGraphRepository,
    tenant_id: UUID,
) -> None:
    symptom = create_node(repo, tenant_id, node_type="SINTOMA", canonical_key="sintoma")
    pathology = create_node(repo, tenant_id, node_type="PATOLOGIA", canonical_key="patologia")
    evidence = create_node(repo, tenant_id, node_type="EVIDENCE", canonical_key="ventas")

    repo.create_edge(
        tenant_id=tenant_id,
        from_node_id=symptom["id"],
        to_node_id=pathology["id"],
        edge_type="INDICATES",
        claim_type="HYPOTHESIS",
    )
    repo.create_edge(
        tenant_id=tenant_id,
        from_node_id=pathology["id"],
        to_node_id=evidence["id"],
        edge_type="REQUIRES_EVIDENCE",
        claim_type="VALIDATED",
    )

    subgraph = repo.get_activation_subgraph(
        tenant_id=tenant_id,
        seed_node_ids=[symptom["id"]],
        edge_types=["INDICATES"],
        claim_types=["HYPOTHESIS"],
        depth=2,
    )

    assert {edge["edge_type"] for edge in subgraph["edges"]} == {"INDICATES"}
    assert {node["id"] for node in subgraph["nodes"]} == {symptom["id"], pathology["id"]}


def test_export_graph_json_includes_nodes_edges_aliases_and_claims(
    repo: InMemorySmartGraphRepository,
    tenant_id: UUID,
) -> None:
    product = create_node(repo, tenant_id, node_type="PRODUCTO", canonical_key="p1")
    supplier = create_node(repo, tenant_id, node_type="PROVEEDOR", canonical_key="s1")
    edge = repo.create_edge(
        tenant_id=tenant_id,
        from_node_id=product["id"],
        to_node_id=supplier["id"],
        edge_type="DEPENDS_ON",
        claim_type="EXTRACTED",
    )
    alias = repo.add_alias(
        tenant_id=tenant_id,
        node_id=product["id"],
        alias="mercadería",
        alias_normalized="mercaderia",
    )
    claim = repo.create_claim(
        tenant_id=tenant_id,
        claim_type="EXTRACTED",
        claim_status="ACTIVE",
        statement="Producto depende de proveedor.",
        edge_id=edge["id"],
    )

    exported = repo.export_graph_json(tenant_id=tenant_id)

    assert exported["tenant_id"] == tenant_id
    assert {node["id"] for node in exported["nodes"]} == {product["id"], supplier["id"]}
    assert [item["id"] for item in exported["edges"]] == [edge["id"]]
    assert [item["id"] for item in exported["aliases"]] == [alias["id"]]
    assert [item["id"] for item in exported["claims"]] == [claim["id"]]


def test_export_graph_json_can_exclude_claims_and_aliases(
    repo: InMemorySmartGraphRepository,
    tenant_id: UUID,
) -> None:
    product = create_node(repo, tenant_id, node_type="PRODUCTO", canonical_key="p1")
    supplier = create_node(repo, tenant_id, node_type="PROVEEDOR", canonical_key="s1")
    edge = repo.create_edge(
        tenant_id=tenant_id,
        from_node_id=product["id"],
        to_node_id=supplier["id"],
        edge_type="DEPENDS_ON",
        claim_type="EXTRACTED",
    )
    repo.add_alias(
        tenant_id=tenant_id,
        node_id=product["id"],
        alias="mercadería",
        alias_normalized="mercaderia",
    )
    repo.create_claim(
        tenant_id=tenant_id,
        claim_type="EXTRACTED",
        claim_status="ACTIVE",
        statement="Producto depende de proveedor.",
        edge_id=edge["id"],
    )

    exported = repo.export_graph_json(
        tenant_id=tenant_id,
        include_claims=False,
        include_aliases=False,
    )

    assert exported["aliases"] == []
    assert exported["claims"] == []


def test_confidence_must_be_between_zero_and_one(
    repo: InMemorySmartGraphRepository,
    tenant_id: UUID,
) -> None:
    with pytest.raises(ValueError, match="confidence"):
        create_node(repo, tenant_id, confidence=1.2)  # type: ignore[call-arg]


def test_zero_uuid_tenant_is_rejected(repo: InMemorySmartGraphRepository) -> None:
    with pytest.raises(ValueError, match="tenant_id"):
        create_node(repo, ZERO_UUID)


def test_records_are_returned_as_copies(
    repo: InMemorySmartGraphRepository,
    tenant_id: UUID,
) -> None:
    node = repo.create_node(
        tenant_id=tenant_id,
        node_type="PRODUCTO",
        canonical_key="p1",
        label="Producto 1",
        metadata={"a": 1},
    )

    node["metadata"]["a"] = 999
    fetched = repo.get_node(tenant_id=tenant_id, node_id=node["id"])

    assert fetched is not None
    assert fetched["metadata"] == {"a": 1}
