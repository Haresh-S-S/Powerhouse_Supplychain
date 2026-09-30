"""
Negative Category Isolation Test Suite for POWER HOUSE Hybrid Regulatory Vector RAG.
Verifies that regulatory evidence retrieved for a business in one category
NEVER leaks or cites statutory provisions from conflicting categories:
- Textile queries NEVER return Food Safety (FSSAI) or Jewellery (HUID/PMLA) citations.
- Restaurant queries NEVER return Textile Committee, Industrial Boilers, or Jewellery citations.
- Jewellery queries NEVER return FSSAI, Restaurant, or Textile Committee citations.
"""
import pytest
from app.rag.retrieval import get_regulatory_retriever


def test_textile_retrieval_excludes_food_and_jewellery():
    """Verify that a Textile enterprise query strictly receives textile/labour citations and zero food or jewellery citations."""
    retriever = get_regulatory_retriever()
    query = "What are the pollution control effluent treatment plant ETP discharge rules and textiles committee returns?"
    res = retriever.retrieve_evidence(
        query=query,
        business_profile_id=1,
        category="clothing_textile",
        top_k=5
    )

    assert res["is_fallback_unretrieved"] is False
    assert len(res["citations"]) > 0

    for c in res["citations"]:
        authority = (c.get("statutory_authority") or "").upper()
        act = (c.get("act") or "").upper()
        preview = (c.get("content_preview") or "").upper()

        # Must not cite FSSAI or Food Safety
        assert "FSSAI" not in authority
        assert "FOOD SAFETY" not in act
        # Must not cite BIS Hallmarking or PMLA
        assert "HUID" not in preview
        assert "BULLION" not in preview


def test_restaurant_retrieval_excludes_textile_and_boilers():
    """Verify that a Restaurant enterprise query strictly receives food/health citations and zero textile or industrial boiler citations."""
    retriever = get_regulatory_retriever()
    query = "What are the FSSAI food business operator licensing and FoSCoS health trade requirements?"
    res = retriever.retrieve_evidence(
        query=query,
        business_profile_id=2,
        category="restaurant",
        top_k=5
    )

    assert res["is_fallback_unretrieved"] is False
    assert len(res["citations"]) > 0

    has_fssai = any("FSSAI" in (c.get("statutory_authority") or "").upper() or "FOOD" in (c.get("act") or "").upper() for c in res["citations"])
    assert has_fssai, "Restaurant query must cite FSSAI / Food Safety provisions"

    for c in res["citations"]:
        authority = (c.get("statutory_authority") or "").upper()
        act = (c.get("act") or "").upper()
        preview = (c.get("content_preview") or "").upper()

        # Must not cite Textile Committee or Boilers
        assert "TEXTILES COMMITTEE" not in act
        assert "BOILERS ACT" not in act
        assert "HUID" not in preview


def test_jewellery_retrieval_excludes_food_and_textile():
    """Verify that a Jewellery enterprise query receives BIS / PMLA citations and zero restaurant or textile citations."""
    retriever = get_regulatory_retriever()
    query = "What are the statutory requirements for 6-digit HUID hallmarking and cash transaction reporting?"
    res = retriever.retrieve_evidence(
        query=query,
        business_profile_id=3,
        category="jewellery",
        top_k=5
    )

    assert res["is_fallback_unretrieved"] is False
    assert len(res["citations"]) > 0

    has_bis_or_pmla = any(
        "BIS" in (c.get("statutory_authority") or "").upper() or
        "PMLA" in (c.get("act") or "").upper() or
        "MONEY LAUNDERING" in (c.get("act") or "").upper() or
        "STANDARDS" in (c.get("act") or "").upper() or
        "HUID" in (c.get("content_preview") or "").upper()
        for c in res["citations"]
    )
    assert has_bis_or_pmla, "Jewellery query must cite BIS Hallmarking or PMLA provisions"

    for c in res["citations"]:
        authority = (c.get("statutory_authority") or "").upper()
        act = (c.get("act") or "").upper()

        # Must not cite Food Safety or Textile
        assert "FSSAI" not in authority
        assert "FOOD SAFETY" not in act
        assert "TEXTILES COMMITTEE" not in act
