import time
from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, model_validator
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.models.business import BusinessProfile
from app.models.regulatory_knowledge import RegulatoryKnowledgeDocument, RegulatoryChunk
from app.rag.retrieval import HybridRegulatoryRetriever
from app.rag.vector_store import VectorStoreService
from app.engine.approval_rules import evaluate_approval_rules

router = APIRouter(prefix="/rag", tags=["Regulatory Vector RAG"])


class RagQueryRequest(BaseModel):
    question: Optional[str] = None
    query: Optional[str] = None
    business_profile_id: Union[str, int]
    top_k: Optional[int] = 5

    @model_validator(mode="after")
    def resolve_fields(self):
        if not self.question and self.query:
            self.question = self.query
        elif not self.query and self.question:
            self.query = self.question
        if not self.question:
            raise ValueError("question or query is required")
        self.business_profile_id = str(self.business_profile_id)
        return self


class RagAdminSourceUpdateRequest(BaseModel):
    source_id: str
    verification_status: str  # INGESTED, REVIEWED, VERIFIED, ACTIVE, RETIRED


def verify_business_ownership(db: Session, current_user: User, business_profile_id: str) -> BusinessProfile:
    """Strict tenant isolation check: verifies profile exists and belongs to authenticated user."""
    profile = db.query(BusinessProfile).filter(
        BusinessProfile.id == business_profile_id
    ).first()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business profile not found"
        )

    if profile.user_id and profile.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: business profile does not belong to the authenticated user."
        )

    return profile


@router.post("/query")
def query_regulatory_rag(
    payload: RagQueryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Hybrid Regulatory Vector RAG query endpoint.
    Retrieves authoritative statutory citations and business document intelligence.
    Enforces strict tenant isolation and provenance tracking.
    """
    start_time = time.perf_counter()

    # 1. Tenant Verification
    profile = verify_business_ownership(db, current_user, payload.business_profile_id)
    category = profile.business_category or profile.industry or "retail"
    city = profile.city or "Tiruppur"
    state = profile.state or "Tamil Nadu"

    # 1. Deterministic Requirement Retrieval (Authoritative)
    deterministic_approvals = evaluate_approval_rules(profile)

    # 2. Hybrid Regulatory Evidence Retrieval
    retrieval_res = HybridRegulatoryRetriever.retrieve_evidence(
        db=db,
        query=payload.question,
        category=category,
        city=city,
        state=state,
        top_k=payload.top_k or 5
    )

    # 3. Tenant-Isolated Business Document Retrieval (Optional Document RAG)
    vector_store = VectorStoreService.get_instance()
    business_doc_results = vector_store.query_business_documents(
        tenant_id=current_user.id,
        business_profile_id=profile.id,
        query_text=payload.question,
        top_k=2
    )

    citations = retrieval_res["citations"]
    has_citations = len(citations) > 0

    # 4. Construct Provenance-Grounded Answer Contract
    # Distinguishes [REGULATORY SOURCE], [BUSINESS PROFILE], [COMPLIANCE RULE], and [BUSINESS DOCUMENT]
    matching_rule = next((a for a in deterministic_approvals if any(t in a["name"].lower() for t in payload.question.lower().split() if len(t) > 3)), None)
    if not matching_rule and deterministic_approvals:
        matching_rule = deterministic_approvals[0]

    rule_name = matching_rule["name"] if matching_rule else "General Statutory Compliance"
    rule_why = matching_rule.get("why_required", "Mandatory statutory compliance under Indian commercial law.") if matching_rule else ""

    top_citation = citations[0] if has_citations else None

    # Structured Answer Sections
    direct_answer = (
        f"Based on verified regulatory statutes for **{profile.business_name}** in {city}, {state}: "
        f"The primary applicable statutory requirement is **{rule_name}**."
    )

    why_it_applies = (
        f"[COMPLIANCE RULE]: {rule_why}\n"
        f"[BUSINESS PROFILE]: Evaluated for {profile.business_name} registered as a '{category.replace('_', ' ').title()}' "
        f"enterprise with operations in {city}, {state}."
    )

    if has_citations and top_citation:
        regulatory_evidence = (
            f"[REGULATORY SOURCE]: Governed under **{top_citation['act_name']}**, **{top_citation['section']}**, "
            f"enforced by the **{top_citation['authority']}** ({top_citation['jurisdiction']}). "
            f"Verification State: **{top_citation['verification_status']}** (Relevance: {int(top_citation['relevance_score'] * 100)}%)."
        )
    else:
        regulatory_evidence = "[REGULATORY SOURCE]: No sufficiently relevant verified regulatory text was retrieved for this specific query. Statutory review is required."

    required_docs_text = (
        ", ".join(matching_rule.get("required_documents_list", ["Identity Proof", "Premises Lease Deed"]))
        if matching_rule and matching_rule.get("required_documents_list") else "Standard statutory identity and operating premises documentation."
    )
    required_documents_section = f"Mandatory evidence: {required_docs_text}."

    current_status_section = (
        f"[WORKFLOW]: Operating status for {rule_name} is currently **{matching_rule.get('status', 'Pending Action')}**."
        if matching_rule else "[WORKFLOW]: Registration setup pending."
    )

    next_action_section = (
        f"[NEXT ACTION]: {matching_rule.get('next_action', 'Review statutory schedule on jurisdictional portal.')}"
        if matching_rule else "[NEXT ACTION]: Complete business registration prerequisites."
    )

    sources_summary = [
        f"{c['title']} ({c['section']}) - {c['authority']} [{c['verification_status']}]"
        for c in citations
    ] if has_citations else ["Statutory registry review required"]

    structured_answer = f"""### DIRECT ANSWER
{direct_answer}

### WHY IT APPLIES
{why_it_applies}

### REGULATORY EVIDENCE
{regulatory_evidence}

### REQUIRED DOCUMENTS
{required_documents_section}

### CURRENT BUSINESS STATUS
{current_status_section}

### NEXT ACTION
{next_action_section}

### SOURCES
* """ + "\n* ".join(sources_summary)

    total_elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

    # Developer / Evaluator RAG Trace diagnostics
    trace_info = {
        "business": profile.business_name,
        "business_category": category,
        "location": f"{city}, {state}",
        "rule_engine_requirements_count": len(deterministic_approvals),
        "primary_rule_selected": rule_name,
        "vector_query": retrieval_res["trace"]["vector_query"],
        "retrieved_count": retrieval_res["trace"]["retrieved_count"],
        "verified_count": retrieval_res["trace"]["verified_count"],
        "rejected_count": retrieval_res["trace"]["rejected_count"],
        "final_citations_count": len(citations),
        "business_documents_retrieved_count": len(business_doc_results),
        "latency_ms": total_elapsed_ms
    }

    return {
        "query": payload.question,
        "business_profile_id": profile.id,
        "category": category,
        "answer": structured_answer,
        "synthesized_answer": structured_answer,
        "direct_answer": direct_answer,
        "answer_context": retrieval_res["answer_context"],
        "citations": citations,
        "sources": retrieval_res["sources"],
        "business_document_evidence": business_doc_results,
        "retrieval_count": len(citations),
        "retrieved_count": retrieval_res["trace"]["retrieved_count"],
        "verified_count": retrieval_res["trace"]["verified_count"],
        "rejected_count": retrieval_res["trace"]["rejected_count"],
        "is_fallback_unretrieved": bool(retrieval_res.get("is_fallback_unretrieved", not has_citations)),
        "fallback_notice": retrieval_res["fallback_notice"],
        "latency_ms": total_elapsed_ms,
        "trace": trace_info
    }


@router.get("/sources")
def list_regulatory_sources(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lists all registered statutory knowledge sources with verification status and version."""
    docs = db.query(RegulatoryKnowledgeDocument).order_by(
        RegulatoryKnowledgeDocument.category,
        RegulatoryKnowledgeDocument.act_name
    ).all()

    return [
        {
            "id": doc.id,
            "source_id": doc.source_id,
            "title": doc.title,
            "authority": doc.authority,
            "jurisdiction": doc.jurisdiction,
            "document_type": doc.document_type,
            "act_name": doc.act_name,
            "section": doc.section,
            "category": doc.category,
            "verification_status": doc.verification_status,
            "version": doc.version,
            "source_url": doc.source_url,
            "content_hash": doc.content_hash,
            "chunks_count": len(doc.chunks),
            "updated_at": doc.updated_at.isoformat()
        }
        for doc in docs
    ]


@router.post("/admin/verify")
def update_source_verification(
    payload: RagAdminSourceUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Administrative source verification endpoint.
    Allows updating verification status (INGESTED, REVIEWED, VERIFIED, ACTIVE, RETIRED).
    """
    doc = db.query(RegulatoryKnowledgeDocument).filter(
        RegulatoryKnowledgeDocument.source_id == payload.source_id
    ).first()

    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Regulatory knowledge document not found"
        )

    valid_statuses = ["INGESTED", "REVIEWED", "VERIFIED", "ACTIVE", "RETIRED"]
    if payload.verification_status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid verification status. Must be one of {valid_statuses}"
        )

    doc.verification_status = payload.verification_status
    for chk in doc.chunks:
        chk.verification_status = payload.verification_status
        db.add(chk)

    db.add(doc)
    db.commit()

    # Update vector store
    vector_store = VectorStoreService.get_instance()
    all_chunks = [
        {
            "chunk_id": chk.chunk_id,
            "content": chk.content,
            "source_id": doc.source_id,
            "act_name": doc.act_name,
            "section": chk.section,
            "chapter": chk.chapter,
            "category": chk.category,
            "jurisdiction": chk.jurisdiction,
            "verification_status": payload.verification_status,
            "content_hash": chk.content_hash
        }
        for chk in doc.chunks
    ]
    vector_store.add_regulatory_chunks(all_chunks)

    return {
        "success": True,
        "source_id": doc.source_id,
        "verification_status": doc.verification_status,
        "message": f"Source '{doc.title}' updated to {doc.verification_status}"
    }
