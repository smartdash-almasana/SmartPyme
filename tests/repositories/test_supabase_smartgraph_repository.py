"""Tests del adapter Supabase para SmartGraph — SmartPyme.

Usa FakeSupabaseClient in-memory, sin red, para validar:
- cliente_id obligatorio y fail-closed.
- tenant_id debe coincidir con cliente_id.
- CRUD básico de nodes, edges, aliases y claims.
- aislamiento multi-tenant.
- reglas anti self-edge.
- reglas de confidence.
- bloqueo de claims HYPOTHESIS/INFERRED/AMBIGUOUS a SUPPORTED sin evidencia/review.
- human review gating.
- activation subgraph.
- export graph.json.
"""
from __future__ import annotations

from uuid import UUID, uuid4

import pytest

from app.repositories.smartgraph_repository_port import SmartGraphRepositoryPort
from app.repositories.supabase_smartgraph_repository import SupabaseSmartGraphRepository


CLIENTE_A_UUID = uuid4()
CLIENTE_B_UUID = uuid4()
CLIENTE_A = str(CLIENTE_A_UUID)
CLIENTE_B = str(CLIENTE_B_UUID)


class _FakeResult:
    def __init__(self, data: list[dict]) -> None:
        self.data = data


class _FakeQueryBuilder:
    """Subset Supabase-like query builder for repository tests."""

    def __init__(self, store: list[dict]) -> None:
        self._store = store
        self._filters: list[tuple[str, object]] = []
        self._mode = "select"
        self._insert_row: dict | None = None
        self._update_patch: dict | None = None
        self._range_start: int | None = None
        self._range_end: int | None = None

    def select(self, cols: str = "*") -> "_FakeQueryBuilder":
        self._mode = "select"
        return self

    def insert(self, row: dict) -> "_FakeQueryBuilder":
        self._mode = "insert"
        self._insert_row = dict(row)
        return self

    def update(self, patch: dict) -> "_FakeQueryBuilder":
        self._mode = "update"
        self._update_patch = dict(patch)
        return self

    def eq(self, col: str, val: object) -> "_FakeQueryBuilder":
        self._filters.append((col, val))
        return self

    def range(self, start: int, end: int) -> "_FakeQueryBuilder":
        self._range_start = start
        self._range_end = end
        return self

    def execute(self) -> _FakeResult:
        if self._mode == "insert":
            if self._insert_row is None:
                raise AssertionError("insert row missing")
            row = dict(self._insert_row)
            row.setdefault("id", str(uuid4()))
            self._store.append(row)
            return _FakeResult([dict(row)])

        if self._mode == "update":
            if self._update_patch is None:
                raise AssertionError("update patch missing")
            matched = self._apply_filters(self._store)
            updated: list[dict] = []
            for row in matched:
                row.update(self._update_patch)
                updated.append(dict(row))
            return _FakeResult(updated)

        result = [dict(row) for row in self._apply_filters(self._store)]
        if self._range_start is not None and self._range_end is not None:
            result = result[self._range_start : self._range_end + 1]
        return _FakeResult(result)

    def _apply_filters(self, rows: list[dict]) -> list[dict]:
        result = list(rows)
        for col, val in self._filters:
            result = [row for row in result if row.get(col) == val]
        return result


class FakeSupabaseClient:
    def __init__(self) -> None:
        self._tables: dict[str, list[dict]] = {}

    def table(self, name: str) -> _FakeQueryBuilder:
        self._tables.setdefault(name, [])
        return _FakeQueryBuilder(self._tables[name])

    def get_rows(self, table: str) -> list[dict]:
        return [dict(row) for row in self._tables.get(table, [])]


@pytest.fixture
def fake_client() -> FakeSupabaseClient:
    return FakeSupabaseClient()


@pytest.fixture
def repo(fake_client: FakeSupabaseClient) -> SupabaseSmartGraphRepository:
    return SupabaseSmartGraphRepository(cliente_id=CLIENTE_A, supabase_client=fake_client)


def create_node(
    repo: SupabaseSmartGraphRepository,
    *,
    tenant_id: UUID = CLIENTE_A_UUID,
    node_type: str = "PRODUCTO",
    canonical_key: str = "producto_a",
    label: str = "Producto A",
) -> dict:
    return repo.create_node(
        tenant_id=tenant_id,
        node_type=node_type,  # type: ignore[arg-type]
        canonical_key=canonical_key,
        label=label,
    )


def test_cliente_id_vacio_lanza_error(fake_client: FakeSupabaseClient) -> None:
    with pytest.raises(ValueError, match="cliente_id"):
        SupabaseSmartGraphRepository(cliente_id="", supabase_client=fake_client)


def test_sin_cliente_inyectado_y_sin_env_falla_cerrado(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SMARTPYME_SUPABASE_URL", raising=False)
    monkeypatch.delenv("SMARTPYME_SUPABASE_KEY", raising=False)

    with pytest.raises(ValueError, match="BLOCKED_ENVIRONMENT_CONTRACT_MISSING"):
        SupabaseSmartGraphRepository(cliente_id=CLIENTE_A)


def test_con_cliente_inyectado_no_requiere_env(
    monkeypatch: pytest.MonkeyPatch,
    fake_client: FakeSupabaseClient,
) -> None:
    monkeypatch.delenv("SMARTPYME_SUPABASE_URL", raising=False)
    monkeypatch.delenv("SMARTPYME_SUPABASE_KEY", raising=False)

    repo = SupabaseSmartGraphRepository(cliente_id=CLIENTE_A, supabase_client=fake_client)

    assert repo.cliente_id == CLIENTE_A


def test_repository_satisface_port(repo: SupabaseSmartGraphRepository) -> None:
    assert isinstance(repo, SmartGraphRepositoryPort)


def test_create_and_get_node(
    repo: SupabaseSmartGraphRepository,
    fake_client: FakeSupabaseClient,
) -> None:
    node = create_node(repo)

    rows = fake_client.get_rows("smartgraph_nodes")
    assert len(rows) == 1
    assert rows[0]["tenant_id"] == CLIENTE_A
    assert rows[0]["canonical_key"] == "producto_a"

    fetched = repo.get_node(tenant_id=CLIENTE_A_UUID, node_id=node["id"])
    assert fetched == node
    assert fetched["tenant_id"] == CLIENTE_A_UUID


def test_tenant_mismatch_falla_cerrado(repo: SupabaseSmartGraphRepository) -> None:
    with pytest.raises(ValueError, match="cliente_id mismatch"):
        create_node(repo, tenant_id=CLIENTE_B_UUID)


def test_get_node_no_filtra_cruzado_entre_tenants(fake_client: FakeSupabaseClient) -> None:
    repo_a = SupabaseSmartGraphRepository(cliente_id=CLIENTE_A, supabase_client=fake_client)
    repo_b = SupabaseSmartGraphRepository(cliente_id=CLIENTE_B, supabase_client=fake_client)
    node = create_node(repo_a)

    assert repo_b.get_node(tenant_id=CLIENTE_B_UUID, node_id=node["id"]) is None


def test_list_nodes_filtra_por_type_y_status(repo: SupabaseSmartGraphRepository) -> None:
    product = create_node(repo, node_type="PRODUCTO", canonical_key="p1")
    create_node(repo, node_type="PROVEEDOR", canonical_key="s1", label="Proveedor 1")

    nodes = repo.list_nodes(tenant_id=CLIENTE_A_UUID, node_type="PRODUCTO")

    assert [node["id"] for node in nodes] == [product["id"]]


def test_create_edge_between_nodes(repo: SupabaseSmartGraphRepository) -> None:
    product = create_node(repo, node_type="PRODUCTO", canonical_key="p1")
    supplier = create_node(repo, node_type="PROVEEDOR", canonical_key="s1", label="Proveedor 1")

    edge = repo.create_edge(
        tenant_id=CLIENTE_A_UUID,
        from_node_id=product["id"],
        to_node_id=supplier["id"],
        edge_type="DEPENDS_ON",
        claim_type="EXTRACTED",
        confidence=0.9,
        evidence_ids=[uuid4()],
    )

    assert edge["from_node_id"] == product["id"]
    assert edge["to_node_id"] == supplier["id"]
    assert edge["edge_type"] == "DEPENDS_ON"
    assert edge["claim_type"] == "EXTRACTED"
    assert len(edge["evidence_ids"]) == 1


def test_create_edge_rejects_self_edge(repo: SupabaseSmartGraphRepository) -> None:
    node = create_node(repo)

    with pytest.raises(ValueError, match="self-edges"):
        repo.create_edge(
            tenant_id=CLIENTE_A_UUID,
            from_node_id=node["id"],
            to_node_id=node["id"],
            edge_type="DEPENDS_ON",
            claim_type="EXTRACTED",
        )


def test_list_edges_for_node_direction(repo: SupabaseSmartGraphRepository) -> None:
    product = create_node(repo, node_type="PRODUCTO", canonical_key="p1")
    supplier = create_node(repo, node_type="PROVEEDOR", canonical_key="s1", label="Proveedor 1")
    edge = repo.create_edge(
        tenant_id=CLIENTE_A_UUID,
        from_node_id=product["id"],
        to_node_id=supplier["id"],
        edge_type="DEPENDS_ON",
        claim_type="EXTRACTED",
    )

    outgoing = repo.list_edges_for_node(
        tenant_id=CLIENTE_A_UUID,
        node_id=product["id"],
        direction="OUT",
    )
    incoming = repo.list_edges_for_node(
        tenant_id=CLIENTE_A_UUID,
        node_id=product["id"],
        direction="IN",
    )

    assert [item["id"] for item in outgoing] == [edge["id"]]
    assert incoming == []


def test_add_alias_and_find_nodes_by_alias(repo: SupabaseSmartGraphRepository) -> None:
    node = create_node(
        repo,
        node_type="PRODUCTO",
        canonical_key="product_stock",
        label="Stock de productos",
    )

    alias = repo.add_alias(
        tenant_id=CLIENTE_A_UUID,
        node_id=node["id"],
        alias="mercadería",
        alias_normalized="mercaderia",
        language="es",
        confidence=0.9,
    )

    matches = repo.find_nodes_by_alias(
        tenant_id=CLIENTE_A_UUID,
        alias_normalized="mercaderia",
    )

    assert alias["node_id"] == node["id"]
    assert [match["id"] for match in matches] == [node["id"]]


def test_create_claim_candidate(repo: SupabaseSmartGraphRepository) -> None:
    node = create_node(repo, node_type="PATOLOGIA", canonical_key="margen_erosionado")

    claim = repo.create_claim(
        tenant_id=CLIENTE_A_UUID,
        claim_type="HYPOTHESIS",
        claim_status="CANDIDATE",
        statement="Puede existir margen erosionado.",
        subject_node_id=node["id"],
        confidence=0.62,
        requires_human_review=True,
    )

    assert claim["claim_type"] == "HYPOTHESIS"
    assert claim["claim_status"] == "CANDIDATE"
    assert claim["requires_human_review"] is True


def test_hypothesis_claim_no_pasa_a_supported_sin_evidencia_o_review(
    repo: SupabaseSmartGraphRepository,
) -> None:
    with pytest.raises(ValueError, match="cannot become SUPPORTED"):
        repo.create_claim(
            tenant_id=CLIENTE_A_UUID,
            claim_type="HYPOTHESIS",
            claim_status="SUPPORTED",
            statement="Puede existir margen erosionado.",
            confidence=0.62,
        )


def test_hypothesis_claim_supported_con_evidencia(repo: SupabaseSmartGraphRepository) -> None:
    claim = repo.create_claim(
        tenant_id=CLIENTE_A_UUID,
        claim_type="HYPOTHESIS",
        claim_status="SUPPORTED",
        statement="Puede existir margen erosionado.",
        evidence_ids=[uuid4()],
    )

    assert claim["claim_status"] == "SUPPORTED"


def test_claim_con_human_review_requiere_review_para_supported(
    repo: SupabaseSmartGraphRepository,
) -> None:
    claim = repo.create_claim(
        tenant_id=CLIENTE_A_UUID,
        claim_type="HYPOTHESIS",
        claim_status="CANDIDATE",
        statement="Puede existir dependencia crítica de proveedor.",
        requires_human_review=True,
        evidence_ids=[uuid4()],
    )

    with pytest.raises(ValueError, match="requires human review"):
        repo.update_claim_status(
            tenant_id=CLIENTE_A_UUID,
            claim_id=claim["id"],
            claim_status="SUPPORTED",
        )


def test_claim_con_human_review_pasa_a_supported_con_review(
    repo: SupabaseSmartGraphRepository,
) -> None:
    claim = repo.create_claim(
        tenant_id=CLIENTE_A_UUID,
        claim_type="HYPOTHESIS",
        claim_status="CANDIDATE",
        statement="Puede existir dependencia crítica de proveedor.",
        requires_human_review=True,
        evidence_ids=[uuid4()],
    )

    updated = repo.update_claim_status(
        tenant_id=CLIENTE_A_UUID,
        claim_id=claim["id"],
        claim_status="SUPPORTED",
        reviewed_by="owner",
        review_decision="approved",
    )

    assert updated["claim_status"] == "SUPPORTED"
    assert updated["reviewed_by"] == "owner"
    assert updated["review_decision"] == "approved"
    assert updated["reviewed_at"] is not None


def test_list_claims_filters(repo: SupabaseSmartGraphRepository) -> None:
    repo.create_claim(
        tenant_id=CLIENTE_A_UUID,
        claim_type="HYPOTHESIS",
        claim_status="CANDIDATE",
        statement="Hipótesis 1",
        requires_human_review=True,
    )
    repo.create_claim(
        tenant_id=CLIENTE_A_UUID,
        claim_type="EXTRACTED",
        claim_status="ACTIVE",
        statement="Dato extraído",
    )

    claims = repo.list_claims(
        tenant_id=CLIENTE_A_UUID,
        claim_type="HYPOTHESIS",
        requires_human_review=True,
    )

    assert len(claims) == 1
    assert claims[0]["statement"] == "Hipótesis 1"


def test_activation_subgraph_respects_depth(repo: SupabaseSmartGraphRepository) -> None:
    symptom = create_node(repo, node_type="SINTOMA", canonical_key="sintoma")
    pathology = create_node(repo, node_type="PATOLOGIA", canonical_key="patologia")
    formula = create_node(repo, node_type="FORMULA", canonical_key="formula")

    repo.create_edge(
        tenant_id=CLIENTE_A_UUID,
        from_node_id=symptom["id"],
        to_node_id=pathology["id"],
        edge_type="INDICATES",
        claim_type="HYPOTHESIS",
    )
    repo.create_edge(
        tenant_id=CLIENTE_A_UUID,
        from_node_id=pathology["id"],
        to_node_id=formula["id"],
        edge_type="REQUIRES_VARIABLE",
        claim_type="VALIDATED",
    )

    depth_1 = repo.get_activation_subgraph(
        tenant_id=CLIENTE_A_UUID,
        seed_node_ids=[symptom["id"]],
        depth=1,
    )
    depth_2 = repo.get_activation_subgraph(
        tenant_id=CLIENTE_A_UUID,
        seed_node_ids=[symptom["id"]],
        depth=2,
    )

    assert {node["id"] for node in depth_1["nodes"]} == {symptom["id"], pathology["id"]}
    assert {node["id"] for node in depth_2["nodes"]} == {
        symptom["id"],
        pathology["id"],
        formula["id"],
    }


def test_export_graph_json(repo: SupabaseSmartGraphRepository) -> None:
    product = create_node(repo, node_type="PRODUCTO", canonical_key="p1")
    supplier = create_node(repo, node_type="PROVEEDOR", canonical_key="s1", label="Proveedor 1")
    edge = repo.create_edge(
        tenant_id=CLIENTE_A_UUID,
        from_node_id=product["id"],
        to_node_id=supplier["id"],
        edge_type="DEPENDS_ON",
        claim_type="EXTRACTED",
    )
    alias = repo.add_alias(
        tenant_id=CLIENTE_A_UUID,
        node_id=product["id"],
        alias="mercadería",
        alias_normalized="mercaderia",
    )
    claim = repo.create_claim(
        tenant_id=CLIENTE_A_UUID,
        claim_type="EXTRACTED",
        claim_status="ACTIVE",
        statement="Producto depende de proveedor.",
        edge_id=edge["id"],
    )

    exported = repo.export_graph_json(tenant_id=CLIENTE_A_UUID)

    assert exported["tenant_id"] == CLIENTE_A_UUID
    assert {node["id"] for node in exported["nodes"]} == {product["id"], supplier["id"]}
    assert [item["id"] for item in exported["edges"]] == [edge["id"]]
    assert [item["id"] for item in exported["aliases"]] == [alias["id"]]
    assert [item["id"] for item in exported["claims"]] == [claim["id"]]


def test_export_graph_json_excluye_claims_y_aliases(repo: SupabaseSmartGraphRepository) -> None:
    product = create_node(repo, node_type="PRODUCTO", canonical_key="p1")
    supplier = create_node(repo, node_type="PROVEEDOR", canonical_key="s1", label="Proveedor 1")
    edge = repo.create_edge(
        tenant_id=CLIENTE_A_UUID,
        from_node_id=product["id"],
        to_node_id=supplier["id"],
        edge_type="DEPENDS_ON",
        claim_type="EXTRACTED",
    )
    repo.add_alias(
        tenant_id=CLIENTE_A_UUID,
        node_id=product["id"],
        alias="mercadería",
        alias_normalized="mercaderia",
    )
    repo.create_claim(
        tenant_id=CLIENTE_A_UUID,
        claim_type="EXTRACTED",
        claim_status="ACTIVE",
        statement="Producto depende de proveedor.",
        edge_id=edge["id"],
    )

    exported = repo.export_graph_json(
        tenant_id=CLIENTE_A_UUID,
        include_claims=False,
        include_aliases=False,
    )

    assert exported["claims"] == []
    assert exported["aliases"] == []


def test_confidence_fuera_de_rango_lanza_error(repo: SupabaseSmartGraphRepository) -> None:
    with pytest.raises(ValueError, match="confidence"):
        repo.create_node(
            tenant_id=CLIENTE_A_UUID,
            node_type="PRODUCTO",
            canonical_key="p1",
            label="Producto 1",
            confidence=1.2,
        )
