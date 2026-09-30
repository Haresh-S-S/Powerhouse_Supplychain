"""
Unit and integration tests for POWER HOUSE Hybrid Regulatory Vector RAG.
Verifies:
- 384-dimensional dense semantic embeddings (StatutoryDenseEmbeddingFunction)
- Statutory-aware hierarchy chunking (Act, Chapter, Section, Subsection)
- ChromaDB vector store persistent collections
- Hybrid 70/30 retrieval scoring and minimum relevance threshold (0.45)
- Grounding gate fallback behavior on ungrounded/gibberish queries
"""
import math
import pytest
from app.rag.chunker import StatutoryChunker
from app.rag.vector_store import StatutoryDenseEmbeddingFunction, get_vector_store
from app.rag.retrieval import get_regulatory_retriever


def test_statutory_dense_embedding_dimension_and_normalization():
    """Verify that StatutoryDenseEmbeddingFunction outputs normalized 384-d vectors."""
    embed_fn = StatutoryDenseEmbeddingFunction(dimension=384)
    texts = [
        "Effluent treatment plant (ETP) standards under Water Act 1974 Section 25",
        "BIS 6-digit alphanumeric Hallmarking Unique Identification (HUID) regulations"
    ]
    embeddings = embed_fn(texts)

    assert len(embeddings) == 2
    for emb in embeddings:
        assert len(emb) == 384
        # Verify L2 normalization (unit magnitude)
        magnitude = math.sqrt(sum(x * x for x in emb))
        assert abs(magnitude - 1.0) < 1e-4, f"Vector magnitude should be 1.0, got {magnitude}"


def test_dense_semantic_similarity():
    """Verify that semantically related texts have higher cosine similarity than unrelated texts."""
    embed_fn = StatutoryDenseEmbeddingFunction(dimension=384)
    v_effluent = embed_fn(["Pollution control effluent discharge standards and ETP treated water"])[0]
    v_water_act = embed_fn(["Water Prevention and Control of Pollution Act Consent to Operate"])[0]
    v_jewellery = embed_fn(["Gold jewellery BIS hallmarking 6-digit HUID assaying centre"])[0]

    # Cosine similarities
    dot_related = sum(a * b for a, b in zip(v_effluent, v_water_act))
    dot_unrelated = sum(a * b for a, b in zip(v_effluent, v_jewellery))

    assert dot_related > dot_unrelated, (
        f"Related texts ({dot_related:.4f}) must have higher similarity than unrelated texts ({dot_unrelated:.4f})"
    )


def test_statutory_chunker_hierarchy_and_hashing():
    """Verify that StatutoryChunker preserves statutory hierarchy and attaches SHA-256 hashes."""
    chunker = StatutoryChunker()
    text = (
        "THE FOOD SAFETY AND STANDARDS ACT, 2006\n\n"
        "CHAPTER IV - GENERAL PRINCIPLES OF FOOD SAFETY\n\n"
        "Section 31. Licensing and registration of food business.\n"
        "(1) No person shall commence or carry on any food business except under a licence.\n"
        "(2) Nothing contained in sub-section (1) shall apply to a petty manufacturer.\n\n"
        "Section 32. Improvement notices.\n"
        "(1) If the designated officer has reasonable ground for believing any food business operator has failed to comply."
    )
    chunks = chunker.chunk_text(
        text=text,
        source_id="test-fssai-doc",
        source_title="Food Safety and Standards Act 2006",
        authority="FSSAI"
    )

    assert len(chunks) >= 2
    for c in chunks:
        assert c.source_document_id == "test-fssai-doc"
        assert c.statutory_authority == "FSSAI"
        assert len(c.content_hash) == 64  # Valid SHA-256 hex string
        assert c.verification_status == "VERIFIED"

    sections = [c.section for c in chunks if c.section]
    assert any("Section 31" in s for s in sections)


def test_vector_store_collections_exist():
    """Verify ChromaDB vector store provides regulatory_knowledge and business_documents collections."""
    vs = get_vector_store()
    reg_col = vs.get_regulatory_collection()
    doc_col = vs.get_business_doc_collection()

    assert reg_col is not None
    assert doc_col is not None

    count = reg_col.count()
    assert count >= 10, f"Expected at least 10 seeded regulatory chunks, got {count}"


def test_hybrid_retrieval_returns_verified_citations():
    """Verify hybrid retrieval returns valid citations above the 0.45 threshold."""
    retriever = get_regulatory_retriever()
    query = "What are the effluent treatment plant ETP discharge rules under the Water Act?"
    res = retriever.retrieve_evidence(
        query=query,
        business_profile_id=1,
        category="clothing_textile",
        top_k=3
    )

    assert res["is_fallback_unretrieved"] is False
    assert len(res["citations"]) > 0
    for citation in res["citations"]:
        assert citation["verification_status"] == "VERIFIED"
        assert citation["composite_relevance"] >= 0.45
        assert citation["statutory_authority"] != ""
        assert citation["act"] != ""


def test_grounding_gate_rejects_gibberish():
    """Verify that gibberish queries (zero statutory keywords) trigger the grounding gate."""
    retriever = get_regulatory_retriever()
    gibberish_query = "xyzqwerty asdfgh zzz123456 foo bar baz"
    res = retriever.retrieve_evidence(
        query=gibberish_query,
        business_profile_id=1,
        category="clothing_textile",
        top_k=3
    )

    assert res["is_fallback_unretrieved"] is True
    assert len(res["citations"]) == 0
    assert "No verified statutory citations met the relevance threshold" in res["synthesized_answer"]
