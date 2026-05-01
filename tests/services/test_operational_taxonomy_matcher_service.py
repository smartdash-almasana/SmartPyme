from __future__ import annotations

import pytest
from app.services.operational_taxonomy_service import OperationalTaxonomyService
from app.services.operational_taxonomy_matcher_service import OperationalTaxonomyMatcherService

@pytest.fixture
def matcher():
    return OperationalTaxonomyMatcherService()

def test_match_kiosco_by_keyword(matcher):
    # TAX_COM_005 has keyword "kiosco"
    msg = "Tengo un kiosco en el centro"
    results = matcher.match(msg)
    assert len(results) > 0
    assert results[0]["item_id"] == "TAX_COM_005"
    assert results[0]["score"] >= 5
    assert any("kiosco" in s for s in results[0]["matched_signals"])

def test_match_ecommerce_mercado_libre(matcher):
    # TAX_COM_002 has keyword "mercado libre"
    msg = "Vendo por mercado libre y me comen las comisiones"
    results = matcher.match(msg)
    assert len(results) > 0
    assert results[0]["item_id"] == "TAX_COM_002"
    # "mercado libre" is a keyword (+5)
    # "las comisiones me comen el margen" is a signal in TAX_COM_002. 
    # The message has "me comen las comisiones" which is slightly different.
    # But "mercado libre" should match.
    assert results[0]["score"] >= 5

def test_match_panaderia(matcher):
    # TAX_IND_001 has keyword "panadería"
    msg = "Mi panadería es tradicional"
    results = matcher.match(msg)
    assert len(results) > 0
    assert results[0]["item_id"] == "TAX_IND_001"

def test_multiple_candidates_ambiguity(matcher):
    # Message that might match multiple items
    # "tienda" (TAX_COM_001) and "kiosco" (TAX_COM_005)
    msg = "Es una tienda que parece un kiosco"
    results = matcher.match(msg, limit=5)
    assert len(results) >= 2
    ids = [r["item_id"] for r in results]
    assert "TAX_COM_001" in ids
    assert "TAX_COM_005" in ids

def test_respect_limit(matcher):
    msg = "tienda mercado libre panaderia kiosco"
    results = matcher.match(msg, limit=2)
    assert len(results) == 2

def test_empty_results_no_signals(matcher):
    msg = "Hola, buen día"
    results = matcher.match(msg)
    assert results == []

def test_include_questions_and_data(matcher):
    msg = "Tengo un kiosco"
    results = matcher.match(msg, limit=1)
    assert len(results) == 1
    assert "suggested_questions" in results[0]
    assert "required_data" in results[0]
    assert isinstance(results[0]["suggested_questions"], list)
    assert isinstance(results[0]["required_data"], list)
    assert len(results[0]["suggested_questions"]) > 0

def test_normalize_accents(matcher):
    # "panadería" has accent
    msg = "Tengo una panaderia"
    results = matcher.match(msg)
    assert len(results) > 0
    assert results[0]["item_id"] == "TAX_IND_001"
