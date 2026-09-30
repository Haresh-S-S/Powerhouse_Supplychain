import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status as http_status, Query
from sqlalchemy.orm import Session

from app.dependencies.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.models.business import BusinessProfile
from app.models.supplier import Supplier, SupplierDocument, SupplyItem, SupplyChainRisk
from app.schemas.supply_chain import (
    SupplierResponse,
    SupplierCreate,
    SupplyItemResponse,
    SupplyItemCreate,
    SupplyChainRiskResponse,
    SupplyChainSummaryResponse,
)
from app.services.supply_chain.risk_service import SupplyChainRiskService
from app.services.supply_chain.agent import SupplyChainAgent
from app.services.supply_chain.demo_data import seed_demo_supply_chain, cleanup_demo_supply_chain

router = APIRouter(prefix="/supply-chain", tags=["Supply Chain Resilience"])


def verify_business_ownership(db: Session, current_user: User, business_profile_id: str) -> BusinessProfile:
    profile = db.query(BusinessProfile).filter(BusinessProfile.id == business_profile_id).first()
    if not profile:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Business profile not found."
        )
    if profile.user_id and profile.user_id != current_user.id:
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: you do not have permission to access supply chain data for this profile."
        )
    return profile


@router.get("/summary", response_model=SupplyChainSummaryResponse)
def get_supply_chain_summary(
    business_profile_id: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = verify_business_ownership(db, current_user, business_profile_id)
    score_data = SupplyChainRiskService.calculate_resilience_score(db, profile.id)

    risks = db.query(SupplyChainRisk).filter(
        SupplyChainRisk.business_id == profile.id,
        SupplyChainRisk.status.notin_(["RESOLVED", "DISMISSED"])
    ).order_by(
        SupplyChainRisk.priority.desc(),
        SupplyChainRisk.detected_at.desc()
    ).limit(5).all()

    top_risk_responses = []
    for r in risks:
        top_risk_responses.append(
            SupplyChainRiskResponse(
                id=r.id,
                business_id=r.business_id,
                supplier_id=r.supplier_id,
                supply_item_id=r.supply_item_id,
                supplier_name=r.supplier.name if r.supplier else None,
                supply_item_name=r.supply_item.name if r.supply_item else None,
                title=r.title,
                category=r.category,
                priority=r.priority,
                severity=r.severity,
                evidence=r.evidence or {},
                issue=r.issue,
                cause=r.cause,
                recommended_action=r.recommended_action,
                estimated_cost=r.estimated_cost,
                estimated_risk_reduction=r.estimated_risk_reduction,
                effort=r.effort,
                confidence=r.confidence,
                status=r.status,
                policy_check_status=r.policy_check_status,
                is_demo=r.is_demo,
                detected_at=r.detected_at,
                updated_at=r.updated_at,
            )
        )

    return SupplyChainSummaryResponse(
        business_id=profile.id,
        total_suppliers=score_data["total_suppliers"],
        critical_suppliers=score_data["critical_suppliers"],
        total_items=score_data["total_items"],
        critical_items=score_data["critical_items"],
        single_source_count=score_data["single_source_count"],
        missing_docs_count=score_data["missing_docs_count"],
        overall_resilience_score=score_data["score"],
        resilience_rating=score_data["rating"],
        active_risks_count=len(risks),
        top_risks=top_risk_responses,
        lead_time_average_days=score_data["lead_time_avg"],
    )


@router.get("/suppliers", response_model=List[SupplierResponse])
def get_suppliers(
    business_profile_id: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = verify_business_ownership(db, current_user, business_profile_id)
    return db.query(Supplier).filter(Supplier.business_id == profile.id).order_by(Supplier.created_at.desc()).all()


@router.post("/suppliers", response_model=SupplierResponse)
def create_supplier(
    supplier_in: SupplierCreate,
    business_profile_id: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = verify_business_ownership(db, current_user, business_profile_id)
    supplier = Supplier(
        id=str(uuid.uuid4()),
        business_id=profile.id,
        name=supplier_in.name,
        supplier_type=supplier_in.supplier_type,
        location=supplier_in.location,
        country=supplier_in.country,
        products_or_materials=supplier_in.products_or_materials,
        dependency_percentage=supplier_in.dependency_percentage,
        lead_time_days=supplier_in.lead_time_days,
        status=supplier_in.status,
        contact_information=supplier_in.contact_information,
        risk_status=supplier_in.risk_status,
        is_demo=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(supplier)
    db.commit()
    db.refresh(supplier)
    return supplier


@router.get("/items", response_model=List[SupplyItemResponse])
def get_supply_items(
    business_profile_id: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = verify_business_ownership(db, current_user, business_profile_id)
    items = db.query(SupplyItem).filter(SupplyItem.business_id == profile.id).order_by(SupplyItem.criticality.desc()).all()
    resp = []
    for item in items:
        r = SupplyItemResponse.from_orm(item)
        r.primary_supplier_name = item.primary_supplier.name if item.primary_supplier else None
        resp.append(r)
    return resp


@router.get("/risks", response_model=List[SupplyChainRiskResponse])
def get_supply_chain_risks(
    business_profile_id: str = Query(...),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = verify_business_ownership(db, current_user, business_profile_id)
    query = db.query(SupplyChainRisk).filter(SupplyChainRisk.business_id == profile.id)
    if status:
        query = query.filter(SupplyChainRisk.status == status)

    risks = query.order_by(SupplyChainRisk.priority.desc(), SupplyChainRisk.detected_at.desc()).all()
    resp = []
    for r in risks:
        resp.append(
            SupplyChainRiskResponse(
                id=r.id,
                business_id=r.business_id,
                supplier_id=r.supplier_id,
                supply_item_id=r.supply_item_id,
                supplier_name=r.supplier.name if r.supplier else None,
                supply_item_name=r.supply_item.name if r.supply_item else None,
                title=r.title,
                category=r.category,
                priority=r.priority,
                severity=r.severity,
                evidence=r.evidence or {},
                issue=r.issue,
                cause=r.cause,
                recommended_action=r.recommended_action,
                estimated_cost=r.estimated_cost,
                estimated_risk_reduction=r.estimated_risk_reduction,
                effort=r.effort,
                confidence=r.confidence,
                status=r.status,
                policy_check_status=r.policy_check_status,
                is_demo=r.is_demo,
                detected_at=r.detected_at,
                updated_at=r.updated_at,
            )
        )
    return resp


@router.get("/risks/{risk_id}", response_model=SupplyChainRiskResponse)
def get_risk_detail(
    risk_id: str,
    business_profile_id: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = verify_business_ownership(db, current_user, business_profile_id)
    r = db.query(SupplyChainRisk).filter(
        SupplyChainRisk.id == risk_id,
        SupplyChainRisk.business_id == profile.id
    ).first()
    if not r:
        raise HTTPException(status_code=404, detail="Supply chain risk not found.")

    return SupplyChainRiskResponse(
        id=r.id,
        business_id=r.business_id,
        supplier_id=r.supplier_id,
        supply_item_id=r.supply_item_id,
        supplier_name=r.supplier.name if r.supplier else None,
        supply_item_name=r.supply_item.name if r.supply_item else None,
        title=r.title,
        category=r.category,
        priority=r.priority,
        severity=r.severity,
        evidence=r.evidence or {},
        issue=r.issue,
        cause=r.cause,
        recommended_action=r.recommended_action,
        estimated_cost=r.estimated_cost,
        estimated_risk_reduction=r.estimated_risk_reduction,
        effort=r.effort,
        confidence=r.confidence,
        status=r.status,
        policy_check_status=r.policy_check_status,
        is_demo=r.is_demo,
        detected_at=r.detected_at,
        updated_at=r.updated_at,
    )


@router.get("/evidence/{risk_id}")
def get_risk_evidence(
    risk_id: str,
    business_profile_id: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = verify_business_ownership(db, current_user, business_profile_id)
    r = db.query(SupplyChainRisk).filter(
        SupplyChainRisk.id == risk_id,
        SupplyChainRisk.business_id == profile.id
    ).first()
    if not r:
        raise HTTPException(status_code=404, detail="Supply chain risk not found.")

    return {
        "risk_id": r.id,
        "title": r.title,
        "category": r.category,
        "evidence": r.evidence or {},
        "issue": r.issue,
        "cause": r.cause,
        "supplier_details": {
            "name": r.supplier.name if r.supplier else None,
            "location": r.supplier.location if r.supplier else None,
            "lead_time_days": r.supplier.lead_time_days if r.supplier else None,
        } if r.supplier else None,
        "supply_item_details": {
            "name": r.supply_item.name if r.supply_item else None,
            "criticality": r.supply_item.criticality if r.supply_item else None,
            "dependency_percentage": r.supply_item.dependency_percentage if r.supply_item else None,
            "alternate_supplier_count": r.supply_item.alternate_supplier_count if r.supply_item else None,
        } if r.supply_item else None
    }


@router.post("/analyze")
def run_supply_chain_analysis(
    business_profile_id: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = verify_business_ownership(db, current_user, business_profile_id)
    analysis_result = SupplyChainAgent.analyze_business_supply_chain(db, profile.id)
    return analysis_result


@router.post("/proposal/{risk_id}")
def create_action_proposal(
    risk_id: str,
    business_profile_id: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = verify_business_ownership(db, current_user, business_profile_id)
    try:
        proposal = SupplyChainAgent.propose_action_for_risk(db, profile.id, risk_id)
        return {
            "status": "SUCCESS",
            "proposal_id": proposal.id,
            "title": proposal.title,
            "risk_level": proposal.risk_level,
            "message": "ActionProposal successfully created. Human confirmation required."
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/demo/seed")
def seed_demo_data(
    business_profile_id: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = verify_business_ownership(db, current_user, business_profile_id)
    result = seed_demo_supply_chain(db, profile.id)
    return result


@router.delete("/demo/cleanup")
def cleanup_demo_data(
    business_profile_id: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = verify_business_ownership(db, current_user, business_profile_id)
    removed_count = cleanup_demo_supply_chain(db, profile.id)
    return {"status": "SUCCESS", "removed_count": removed_count}
