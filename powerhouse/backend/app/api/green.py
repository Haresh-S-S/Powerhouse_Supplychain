import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status as http_status, Query
from sqlalchemy.orm import Session

from app.dependencies.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.models.business import BusinessProfile
from app.models.green_opportunity import GreenOpportunity
from app.models.emission_factor import EmissionFactor
from app.models.green_impact import GreenImpactMeasurement
from app.models.agent_run import AgentRun
from app.models.green_metric import GreenOperationalMetric
from app.schemas.green import (
    GreenSummaryResponse,
    GreenOpportunityResponse,
    GreenScoreDetailResponse,
    GreenImpactResponse,
    GreenImpactVerifyRequest,
    AgentRunResponse,
    EmissionFactorResponse,
)
from app.services.green.orchestrator import GreenAgentOrchestrator
from app.services.green.score_service import GreenScoreService
from app.services.green.emission_factors import EmissionFactorService
from app.services.green.demo_data import seed_demo_operational_metrics
from app.services.proposal_service import ProposalService

router = APIRouter(prefix="/green", tags=["Green Industry Flow AI"])


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
            detail="Access forbidden: you do not have permission to access green intelligence for this profile."
        )
    return profile


# ----------------------------------------------------
# 1. Summary & Score Endpoints
# ----------------------------------------------------
@router.get("/summary", response_model=GreenSummaryResponse)
def get_green_summary(
    business_profile_id: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = verify_business_ownership(db, current_user, business_profile_id)
    score_data = GreenScoreService.calculate_green_score(db, profile.id)

    # Fetch active opportunities
    opps = (
        db.query(GreenOpportunity)
        .filter(GreenOpportunity.business_profile_id == profile.id)
        .order_by(GreenOpportunity.created_at.desc())
        .all()
    )

    # Calculate cumulative potential savings from detected opportunities
    total_cost_savings = 0.0
    total_energy_kwh = 0.0
    total_carbon_kg = 0.0

    has_cost = False
    has_energy = False
    has_carbon = False

    for op in opps:
        if op.estimated_cost_impact and isinstance(op.estimated_cost_impact, dict) and op.estimated_cost_impact.get("value"):
            total_cost_savings += float(op.estimated_cost_impact["value"])
            has_cost = True
        if op.estimated_energy_impact and isinstance(op.estimated_energy_impact, dict) and op.estimated_energy_impact.get("value"):
            total_energy_kwh += float(op.estimated_energy_impact["value"])
            has_energy = True
        if op.estimated_carbon_impact and isinstance(op.estimated_carbon_impact, dict) and op.estimated_carbon_impact.get("value"):
            total_carbon_kg += float(op.estimated_carbon_impact["value"])
            has_carbon = True

    cost_str = f"₹{int(total_cost_savings):,}/mo" if has_cost else "DATA REQUIRED"
    energy_str = f"{int(total_energy_kwh):,} kWh/mo" if has_energy else "Insufficient energy data"
    carbon_str = f"{total_carbon_kg:,.1f} kgCO2e/mo" if has_carbon else "Emission factor unconfigured"

    # Evaluate Data Quality
    metrics_count = db.query(GreenOperationalMetric).filter(GreenOperationalMetric.business_profile_id == profile.id).count()
    if metrics_count >= 4:
        data_quality = "HIGH"
        data_quality_notes = "Operational compute, energy, and workflow telemetry are actively monitored."
    elif metrics_count > 0:
        data_quality = "MEDIUM"
        data_quality_notes = "Partial operational telemetry is connected. Additional telemetry recommended for higher fidelity."
    else:
        data_quality = "INSUFFICIENT"
        data_quality_notes = "No real-time energy or compute monitors connected. Demonstrating with baseline statutory models."

    verified_count = (
        db.query(GreenImpactMeasurement)
        .filter(
            GreenImpactMeasurement.business_profile_id == profile.id,
            GreenImpactMeasurement.verification_status == "VERIFIED"
        )
        .count()
    )

    return {
        "business_profile_id": profile.id,
        "green_score": score_data["score"],
        "score_rating": score_data["rating"],
        "potential_cost_savings": cost_str,
        "energy_opportunity": energy_str,
        "estimated_carbon_reduction": carbon_str,
        "open_opportunities_count": len([o for o in opps if o.status in ["DETECTED", "UNDER_REVIEW"]]),
        "verified_impacts_count": verified_count,
        "data_quality": data_quality,
        "data_quality_notes": data_quality_notes,
        "top_opportunities": opps[:5],
    }


@router.get("/score", response_model=GreenScoreDetailResponse)
def get_green_score_detail(
    business_profile_id: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = verify_business_ownership(db, current_user, business_profile_id)
    return GreenScoreService.calculate_green_score(db, profile.id)


# ----------------------------------------------------
# 2. Opportunities Endpoints
# ----------------------------------------------------
@router.get("/opportunities", response_model=List[GreenOpportunityResponse])
def list_opportunities(
    business_profile_id: str = Query(...),
    category: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = verify_business_ownership(db, current_user, business_profile_id)
    query = db.query(GreenOpportunity).filter(GreenOpportunity.business_profile_id == profile.id)
    if category and category != "All":
        query = query.filter(GreenOpportunity.category == category)
    if status and status != "All":
        query = query.filter(GreenOpportunity.status == status)

    return query.order_by(GreenOpportunity.created_at.desc()).all()


@router.get("/opportunities/{opportunity_id}", response_model=GreenOpportunityResponse)
def get_opportunity(
    opportunity_id: str,
    business_profile_id: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    verify_business_ownership(db, current_user, business_profile_id)
    opp = db.query(GreenOpportunity).filter(
        GreenOpportunity.id == opportunity_id,
        GreenOpportunity.business_profile_id == business_profile_id
    ).first()
    if not opp:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="Opportunity not found.")
    return opp


@router.get("/opportunities/{opportunity_id}/evidence")
def get_opportunity_evidence(
    opportunity_id: str,
    business_profile_id: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    verify_business_ownership(db, current_user, business_profile_id)
    opp = db.query(GreenOpportunity).filter(
        GreenOpportunity.id == opportunity_id,
        GreenOpportunity.business_profile_id == business_profile_id
    ).first()
    if not opp:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="Opportunity not found.")
    return {
        "opportunity_id": opp.id,
        "title": opp.title,
        "agent_type": opp.agent_type,
        "confidence": opp.confidence,
        "evidence": opp.evidence,
    }


@router.get("/opportunities/{opportunity_id}/trace")
def get_opportunity_trace(
    opportunity_id: str,
    business_profile_id: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    verify_business_ownership(db, current_user, business_profile_id)
    opp = db.query(GreenOpportunity).filter(
        GreenOpportunity.id == opportunity_id,
        GreenOpportunity.business_profile_id == business_profile_id
    ).first()
    if not opp:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="Opportunity not found.")

    first_evidence = opp.evidence[0] if opp.evidence and len(opp.evidence) > 0 else {}
    obs_summary = first_evidence.get("evidence_summary", "Operational data points collected.")
    source_type = first_evidence.get("source_type", "SYSTEM_METRIC")

    decision_trace = [
        {"stage": "Observed Data", "detail": obs_summary, "source": source_type},
        {"stage": "Detected Pattern", "detail": opp.detected_issue, "severity": opp.severity},
        {"stage": "Root Cause Analysis", "detail": opp.cause, "agent": opp.agent_type},
        {"stage": "Recommended Action", "detail": opp.recommended_action, "effort": opp.implementation_effort},
        {"stage": "Impact Calculation Method", "detail": (opp.estimated_energy_impact or {}).get("formula") or "Deterministic emission model", "assumptions": (opp.estimated_energy_impact or {}).get("assumptions") or "Verified standards"},
        {"stage": "Policy Validation Check", "status": opp.policy_status, "detail": opp.policy_notes or "Passed enterprise operational guidelines"},
        {"stage": "Confidence & Scoring", "score": f"{int(opp.confidence * 100)}%", "priority": opp.priority},
    ]

    return {
        "opportunity_id": opp.id,
        "title": opp.title,
        "decision_trace": decision_trace,
    }


# ----------------------------------------------------
# 3. Agent Orchestration & Runs
# ----------------------------------------------------
@router.post("/agent/run")
def trigger_agent_run(
    business_profile_id: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = verify_business_ownership(db, current_user, business_profile_id)
    res = GreenAgentOrchestrator.run_orchestration(db, profile)
    return {
        "message": f"Orchestration completed with status: {res['status']}",
        "run_id": res["run_id"],
        "opportunities_generated": res["output_count"],
        "trace_steps": res["trace_steps"],
    }


@router.get("/agent-runs", response_model=List[AgentRunResponse])
def get_agent_runs(
    business_profile_id: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = verify_business_ownership(db, current_user, business_profile_id)
    return (
        db.query(AgentRun)
        .filter(AgentRun.business_profile_id == profile.id)
        .order_by(AgentRun.started_at.desc())
        .limit(20)
        .all()
    )


# ----------------------------------------------------
# 4. Human-in-the-Loop Action Proposal Creation
# ----------------------------------------------------
@router.post("/opportunities/{opportunity_id}/proposal")
def create_action_proposal_from_opportunity(
    opportunity_id: str,
    business_profile_id: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    verify_business_ownership(db, current_user, business_profile_id)
    opp = db.query(GreenOpportunity).filter(
        GreenOpportunity.id == opportunity_id,
        GreenOpportunity.business_profile_id == business_profile_id
    ).first()
    if not opp:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="Opportunity not found.")

    proposal_data = {
        "action_type": "CREATE_GREEN_TASK",
        "title": f"Implement: {opp.title}",
        "reason": f"AI Sustainability finding: {opp.detected_issue} Recommended action: {opp.recommended_action}",
        "affected_entity_type": "green_opportunity",
        "affected_entity_id": opp.id,
        "changes": {
            "category": "Green Operations",
            "opportunity_id": opp.id,
            "opportunity_title": opp.title,
            "recommended_action": opp.recommended_action,
            "status": {"from": opp.status, "to": "TASK_CREATED"}
        },
        "risk_level": "Low" if opp.policy_status == "PASS" else "Medium",
        "created_by": f"{opp.agent_type} (Green Flow AI)"
    }

    proposal = ProposalService.create_proposal(db, business_profile_id, proposal_data)
    opp.status = "UNDER_REVIEW"
    opp.reviewed_at = datetime.utcnow()
    db.add(opp)
    db.commit()
    db.refresh(opp)

    return {
        "message": "Action proposal created. Awaiting human confirmation in Action Proposals.",
        "proposal_id": proposal.id,
        "opportunity_id": opp.id,
        "status": opp.status,
    }


# ----------------------------------------------------
# 5. Impact Measurement & Verification
# ----------------------------------------------------
@router.get("/impact", response_model=List[GreenImpactResponse])
def list_impact_measurements(
    business_profile_id: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = verify_business_ownership(db, current_user, business_profile_id)
    return (
        db.query(GreenImpactMeasurement)
        .filter(GreenImpactMeasurement.business_profile_id == profile.id)
        .order_by(GreenImpactMeasurement.created_at.desc())
        .all()
    )


@router.post("/impact/{impact_id}/verify", response_model=GreenImpactResponse)
def verify_impact_measurement(
    impact_id: str,
    payload: GreenImpactVerifyRequest,
    business_profile_id: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    verify_business_ownership(db, current_user, business_profile_id)
    impact = db.query(GreenImpactMeasurement).filter(
        GreenImpactMeasurement.id == impact_id,
        GreenImpactMeasurement.business_profile_id == business_profile_id
    ).first()
    if not impact:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="Impact measurement record not found.")

    measured = payload.measured_value
    base = impact.baseline_value
    abs_change = round(base - measured, 2)
    pct_change = round((abs_change / base) * 100.0, 1) if base > 0 else 0.0

    impact.measured_value = measured
    impact.absolute_change = abs_change
    impact.percentage_change = pct_change
    impact.verification_status = "VERIFIED"
    impact.verified_at = datetime.utcnow()
    if payload.assumptions:
        impact.assumptions = payload.assumptions
    if payload.is_demo:
        impact.is_demo = True

    # Mark parent opportunity as VERIFIED
    if impact.opportunity:
        impact.opportunity.status = "VERIFIED"
        impact.opportunity.completed_at = datetime.utcnow()
        db.add(impact.opportunity)

    db.add(impact)
    db.commit()
    db.refresh(impact)
    return impact


# ----------------------------------------------------
# 6. Emission Factors Registry
# ----------------------------------------------------
@router.get("/emission-factors", response_model=List[EmissionFactorResponse])
def get_emission_factors(db: Session = Depends(get_db)):
    return EmissionFactorService.get_all_factors(db)


# ----------------------------------------------------
# 7. Demo Data Seeder
# ----------------------------------------------------
@router.post("/demo/seed")
def seed_demo_data(
    business_profile_id: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = verify_business_ownership(db, current_user, business_profile_id)
    seed_demo_operational_metrics(db, profile.id)
    # Immediately trigger orchestration over the newly seeded demo telemetry
    res = GreenAgentOrchestrator.run_orchestration(db, profile)
    return {
        "message": "Demo operational metrics successfully seeded and analyzed under '[DEMO DATA]' label.",
        "opportunities_generated": res["output_count"],
    }
