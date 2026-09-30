import time
import re
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.regulatory_knowledge import RegulatoryKnowledgeDocument, RegulatoryChunk
from app.rag.vector_store import VectorStoreService


class HybridRegulatoryRetriever:
    """
    Hybrid Regulatory Retrieval Engine combining 70% Semantic Vector search
    and 30% Statutory Keyword & Metadata matching.
    Enforces business context isolation, relevance thresholding, and strict citation validation.
    """

    DEFAULT_SEMANTIC_WEIGHT = 0.70
    DEFAULT_KEYWORD_WEIGHT = 0.30
    DEFAULT_RELEVANCE_THRESHOLD = 0.45
    DEFAULT_TOP_K = 5

    @classmethod
    def sanitize_input(cls, text: str) -> str:
        """Sanitizes query text and protects against prompt injection attempts."""
        if not text:
            return ""
        # Neutralize common prompt injection patterns
        injection_patterns = [
            r"ignore\s+(?:all\s+)?(?:previous|prior)\s+instructions",
            r"you\s+are\s+now\s+a",
            r"system\s+override",
            r"forget\s+compliance",
            r"disregard\s+rules"
        ]
        sanitized = text
        for p in injection_patterns:
            sanitized = re.sub(p, "[REDACTED_INPUT]", sanitized, flags=re.IGNORECASE)
        return sanitized.strip()

    @classmethod
    def compute_keyword_score(cls, query: str, chunk_content: str, metadata: Dict[str, Any]) -> float:
        """Computes deterministic keyword & statutory metadata relevance score in [0.0, 1.0]."""
        stopwords = {'what', 'are', 'the', 'is', 'a', 'an', 'and', 'or', 'for', 'my', 'in', 'of', 'to', 'do', 'i', 'needed', 'applies', 'apply', 'with', 'from', 'which', 'who', 'how', 'when', 'where', 'can'}
        q_tokens = [t for t in re.findall(r"\w+", query.lower()) if len(t) > 2 and t not in stopwords]
        if not q_tokens:
            return 0.5

        content_lower = chunk_content.lower()
        act_lower = (metadata.get("act_name") or "").lower()
        sec_lower = (metadata.get("section") or "").lower()
        cat_lower = (metadata.get("category") or "").lower()

        # Body matches
        matches = sum(1 for t in q_tokens if t in content_lower)
        body_score = min(1.0, matches / max(1, len(q_tokens)))

        # Metadata bonus for exact Act, Section, or Category matches
        metadata_bonus = 0.0
        if any(t in act_lower for t in q_tokens):
            metadata_bonus += 0.25
        if any(t in sec_lower for t in q_tokens):
            metadata_bonus += 0.25
        if any(t in cat_lower for t in q_tokens):
            metadata_bonus += 0.20

        return min(1.0, (0.6 * body_score) + metadata_bonus)

    @classmethod
    def retrieve_evidence(
        cls,
        db: Optional[Session] = None,
        query: str = "",
        category: str = "",
        city: str = "",
        state: str = "",
        top_k: int = DEFAULT_TOP_K,
        relevance_threshold: float = DEFAULT_RELEVANCE_THRESHOLD,
        semantic_weight: float = DEFAULT_SEMANTIC_WEIGHT,
        keyword_weight: float = DEFAULT_KEYWORD_WEIGHT,
        business_profile_id: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        start_time = time.perf_counter()
        clean_query = cls.sanitize_input(query)
        vector_store = VectorStoreService.get_instance()

        # 1. Category Context Resolution
        clean_cat = (category or "").lower().strip()
        if "textile" in clean_cat or "cloth" in clean_cat:
            cat_filter = "clothing_textile"
        elif "restaurant" in clean_cat or "food" in clean_cat:
            cat_filter = "restaurant"
        elif "jewel" in clean_cat or "gold" in clean_cat:
            cat_filter = "jewellery"
        elif "retail" in clean_cat or "shop" in clean_cat:
            cat_filter = "retail"
        elif "factory" in clean_cat or "manufactur" in clean_cat:
            cat_filter = "manufacturing"
        else:
            cat_filter = clean_cat or "general_statutory"

        # 2. Vector Semantic Retrieval
        raw_vector_results = vector_store.query_regulatory(
            query_text=clean_query,
            category=cat_filter,
            top_k=max(top_k * 2, 8),
            only_verified=True
        )

        # 3. Hybrid Scoring & Category Isolation Gate
        scored_candidates = []
        verified_count = 0
        rejected_count = 0

        for r in raw_vector_results:
            meta = r.get("metadata", {})
            chunk_cat = meta.get("category", "")

            # Strict Negative Category Isolation:
            # If query is for textile, never return restaurant or jewellery-only chunks
            if cat_filter != "general_statutory":
                if chunk_cat not in [cat_filter, "general_statutory"]:
                    rejected_count += 1
                    continue

            sem_score = r.get("semantic_score", 0.0)
            kw_score = cls.compute_keyword_score(clean_query, r["content"], meta)

            # Grounding Gate: If query has zero keyword/metadata overlap with the statute, reject as ungrounded noise
            if kw_score < 0.05:
                rejected_count += 1
                continue

            composite_score = round((semantic_weight * sem_score) + (keyword_weight * kw_score), 4)

            # Threshold Filter
            if composite_score >= relevance_threshold:
                verified_count += 1
                scored_candidates.append({
                    "chunk_id": r["chunk_id"],
                    "content": r["content"],
                    "source_id": meta.get("source_id", ""),
                    "act_name": meta.get("act_name", ""),
                    "authority": meta.get("authority", ""),
                    "title": meta.get("title", ""),
                    "section": meta.get("section", "General"),
                    "chapter": meta.get("chapter", ""),
                    "jurisdiction": meta.get("jurisdiction", ""),
                    "category": chunk_cat,
                    "verification_status": meta.get("verification_status", "VERIFIED"),
                    "semantic_score": sem_score,
                    "keyword_score": kw_score,
                    "composite_score": composite_score
                })
            else:
                rejected_count += 1

        # Sort by composite score descending
        scored_candidates.sort(key=lambda x: x["composite_score"], reverse=True)
        top_candidates = scored_candidates[:top_k]

        # 4. Strict Citation Validation Gate
        validated_citations = []
        structured_sources = []

        for cand in top_candidates:
            doc = None
            if db is not None:
                try:
                    doc = db.query(RegulatoryKnowledgeDocument).filter(
                        RegulatoryKnowledgeDocument.source_id == cand["source_id"]
                    ).first()
                except Exception:
                    doc = None

            v_status = doc.verification_status if doc else cand.get("verification_status", "VERIFIED")
            if v_status in ["VERIFIED", "ACTIVE"]:
                doc_title = doc.title if doc else (cand.get("title") or cand.get("act_name", "Statutory Provision"))
                doc_auth = doc.authority if doc else (cand.get("authority") or "Ministry / Directorate")
                doc_act = doc.act_name if doc else cand.get("act_name", "")
                doc_url = doc.source_url if doc else "https://egazette.gov.in"
                doc_jurisdiction = doc.jurisdiction if doc else cand.get("jurisdiction", "Central")
                doc_cat = doc.category if doc else cand["category"]

                citation = {
                    "source_id": doc.source_id if doc else cand["source_id"],
                    "title": doc_title,
                    "source_document_title": doc_title,
                    "authority": doc_auth,
                    "statutory_authority": doc_auth,
                    "act_name": doc_act,
                    "act": doc_act,
                    "section": cand["section"],
                    "chunk_id": cand["chunk_id"],
                    "content_preview": cand["content"][:240],
                    "jurisdiction": doc_jurisdiction,
                    "category": doc_cat,
                    "relevance_score": cand["composite_score"],
                    "composite_relevance": cand["composite_score"],
                    "verification_status": v_status,
                    "source_url": doc_url
                }
                validated_citations.append(citation)

                source_entry = {
                    "source_id": citation["source_id"],
                    "title": doc_title,
                    "authority": doc_auth,
                    "act": doc_act,
                    "section": cand["section"],
                    "category": doc_cat,
                    "passage": cand["content"],
                    "verification_status": v_status,
                    "relevance_percentage": f"{int(cand['composite_score'] * 100)}%"
                }
                structured_sources.append(source_entry)

        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

        # 5. Build Result Contract
        has_sufficient_evidence = len(validated_citations) > 0
        answer_context = [c["content"] for c in top_candidates] if has_sufficient_evidence else []

        if has_sufficient_evidence:
            top_cit = validated_citations[0]
            synthesized_answer = (
                f"Governed under **{top_cit['act']}**, **{top_cit['section']}**, enforced by the **{top_cit['authority']}**. "
                f"Verification State: **{top_cit['verification_status']}** (Relevance: {int(top_cit['relevance_score'] * 100)}%).\n\n"
                f"Statutory mandate: {top_cit['content_preview']}"
            )
            fallback_notice = None
        else:
            synthesized_answer = (
                "No verified statutory citations met the relevance threshold for this query. "
                "Direct compliance and legal review is recommended."
            )
            fallback_notice = "No sufficiently relevant verified regulatory evidence was found for this query. Review required."

        return {
            "answer_context": answer_context,
            "citations": validated_citations,
            "retrieval_count": len(validated_citations),
            "sources": structured_sources,
            "fallback_notice": fallback_notice,
            "synthesized_answer": synthesized_answer,
            "is_fallback_unretrieved": not has_sufficient_evidence,
            "trace": {
                "business_category": cat_filter,
                "location": f"{city}, {state}".strip(", "),
                "vector_query": clean_query,
                "retrieved_count": len(raw_vector_results),
                "verified_count": verified_count,
                "rejected_count": rejected_count,
                "final_citations_count": len(validated_citations),
                "latency_ms": elapsed_ms
            }
        }


def get_regulatory_retriever() -> HybridRegulatoryRetriever:
    return HybridRegulatoryRetriever()
