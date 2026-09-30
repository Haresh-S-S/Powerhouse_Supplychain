import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status as http_status, Query
from sqlalchemy.orm import Session

from app.dependencies.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.models.business import BusinessProfile
from app.models.workforce import EmployeeProfile, RoleProfile, SkillGap, LearningPath
from app.schemas.workforce import (
    EmployeeProfileResponse,
    EmployeeProfileCreate,
    RoleProfileResponse,
    RoleProfileCreate,
    SkillGapResponse,
    LearningPathResponse,
    WorkforceSummaryResponse,
)
from app.services.workforce.intelligence_service import WorkforceIntelligenceService
from app.services.workforce.agent import WorkforceAgent
from app.services.workforce.demo_data import seed_demo_workforce, cleanup_demo_workforce

router = APIRouter(prefix="/workforce", tags=["Workforce Intelligence"])


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
            detail="Access forbidden: you do not have permission to access workforce data for this profile."
        )
    return profile


@router.get("/summary", response_model=WorkforceSummaryResponse)
def get_workforce_summary(
    business_profile_id: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = verify_business_ownership(db, current_user, business_profile_id)
    summary_data = WorkforceIntelligenceService.calculate_workforce_summary(db, profile.id)

    gaps = db.query(SkillGap).filter(
        SkillGap.business_id == profile.id,
        SkillGap.status.notin_(["RESOLVED", "WAIVED"])
    ).order_by(SkillGap.created_at.desc()).limit(5).all()

    top_gaps = []
    for g in gaps:
        top_gaps.append(
            SkillGapResponse(
                id=g.id,
                business_id=g.business_id,
                employee_id=g.employee_id,
                role_id=g.role_id,
                employee_reference=g.employee.employee_reference if g.employee else None,
                role_name=g.role.role_name if g.role else None,
                department=g.employee.department if g.employee else None,
                current_skill=g.current_skill,
                required_skill=g.required_skill,
                gap_level=g.gap_level,
                recommended_action=g.recommended_action,
                status=g.status,
                accessibility_accommodations=g.employee.accessibility_preferences if g.employee else [],
                is_demo=g.is_demo,
                created_at=g.created_at,
                updated_at=g.updated_at,
            )
        )

    paths = db.query(LearningPath).filter(
        LearningPath.business_id == profile.id
    ).order_by(LearningPath.created_at.desc()).limit(5).all()

    active_paths = []
    for p in paths:
        active_paths.append(
            LearningPathResponse(
                id=p.id,
                business_id=p.business_id,
                employee_id=p.employee_id,
                employee_reference=p.employee.employee_reference if p.employee else None,
                target_role=p.target_role,
                title=p.title,
                skill_sequence=p.skill_sequence or [],
                progress=p.progress,
                status=p.status,
                estimated_weeks=p.estimated_weeks,
                accessibility_accommodations=p.accessibility_accommodations or [],
                is_demo=p.is_demo,
                created_at=p.created_at,
                updated_at=p.updated_at,
            )
        )

    return WorkforceSummaryResponse(
        business_id=profile.id,
        total_employees=summary_data["total_employees"],
        total_roles=summary_data["total_roles"],
        open_skill_gaps_count=summary_data["open_skill_gaps"],
        active_learning_paths_count=summary_data["active_paths"],
        average_skill_coverage_percent=summary_data["skill_coverage_pct"],
        accessibility_supported_count=summary_data["accessibility_count"],
        top_skill_gaps=top_gaps,
        active_paths=active_paths,
    )


@router.get("/employees", response_model=List[EmployeeProfileResponse])
def get_employees(
    business_profile_id: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = verify_business_ownership(db, current_user, business_profile_id)
    return db.query(EmployeeProfile).filter(EmployeeProfile.business_id == profile.id).order_by(EmployeeProfile.created_at.desc()).all()


@router.post("/employees", response_model=EmployeeProfileResponse)
def create_employee(
    emp_in: EmployeeProfileCreate,
    business_profile_id: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = verify_business_ownership(db, current_user, business_profile_id)
    emp = EmployeeProfile(
        id=str(uuid.uuid4()),
        business_id=profile.id,
        employee_reference=emp_in.employee_reference,
        role=emp_in.role,
        department=emp_in.department,
        experience_years=emp_in.experience_years,
        current_skills=emp_in.current_skills,
        preferred_learning_areas=emp_in.preferred_learning_areas,
        employment_status=emp_in.employment_status,
        accessibility_preferences=emp_in.accessibility_preferences,
        is_demo=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(emp)
    db.commit()
    db.refresh(emp)
    return emp


@router.get("/roles", response_model=List[RoleProfileResponse])
def get_roles(
    business_profile_id: str = Query(...),
    auto_seed: bool = Query(True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = verify_business_ownership(db, current_user, business_profile_id)
    roles = db.query(RoleProfile).filter(RoleProfile.business_id == profile.id).order_by(RoleProfile.created_at.desc()).all()
    if not roles and auto_seed:
        from app.services.workforce.demo_data import seed_demo_workforce
        seed_demo_workforce(db, profile.id)
        roles = db.query(RoleProfile).filter(RoleProfile.business_id == profile.id).order_by(RoleProfile.created_at.desc()).all()
    return roles


@router.post("/roles", response_model=RoleProfileResponse)
def create_role(
    role_in: RoleProfileCreate,
    business_profile_id: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = verify_business_ownership(db, current_user, business_profile_id)
    role = RoleProfile(
        id=str(uuid.uuid4()),
        business_id=profile.id,
        role_name=role_in.role_name,
        department=role_in.department,
        required_skills=role_in.required_skills,
        optional_skills=role_in.optional_skills,
        is_demo=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(role)
    db.commit()
    db.refresh(role)
    return role


@router.get("/skill-gaps", response_model=List[SkillGapResponse])
def get_skill_gaps(
    business_profile_id: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = verify_business_ownership(db, current_user, business_profile_id)
    gaps = db.query(SkillGap).filter(SkillGap.business_id == profile.id).order_by(SkillGap.created_at.desc()).all()
    resp = []
    for g in gaps:
        resp.append(
            SkillGapResponse(
                id=g.id,
                business_id=g.business_id,
                employee_id=g.employee_id,
                role_id=g.role_id,
                employee_reference=g.employee.employee_reference if g.employee else None,
                role_name=g.role.role_name if g.role else None,
                department=g.employee.department if g.employee else None,
                current_skill=g.current_skill,
                required_skill=g.required_skill,
                gap_level=g.gap_level,
                recommended_action=g.recommended_action,
                status=g.status,
                accessibility_accommodations=g.employee.accessibility_preferences if g.employee else [],
                is_demo=g.is_demo,
                created_at=g.created_at,
                updated_at=g.updated_at,
            )
        )
    return resp


@router.get("/learning-paths", response_model=List[LearningPathResponse])
def get_learning_paths(
    business_profile_id: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = verify_business_ownership(db, current_user, business_profile_id)
    paths = db.query(LearningPath).filter(LearningPath.business_id == profile.id).order_by(LearningPath.created_at.desc()).all()
    resp = []
    for p in paths:
        resp.append(
            LearningPathResponse(
                id=p.id,
                business_id=p.business_id,
                employee_id=p.employee_id,
                employee_reference=p.employee.employee_reference if p.employee else None,
                target_role=p.target_role,
                title=p.title,
                skill_sequence=p.skill_sequence or [],
                progress=p.progress,
                status=p.status,
                estimated_weeks=p.estimated_weeks,
                accessibility_accommodations=p.accessibility_accommodations or [],
                is_demo=p.is_demo,
                created_at=p.created_at,
                updated_at=p.updated_at,
            )
        )
    return resp


@router.get("/evidence/{gap_id}")
def get_skill_gap_evidence(
    gap_id: str,
    business_profile_id: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = verify_business_ownership(db, current_user, business_profile_id)
    g = db.query(SkillGap).filter(
        SkillGap.id == gap_id,
        SkillGap.business_id == profile.id
    ).first()
    if not g:
        raise HTTPException(status_code=404, detail="Skill gap not found.")

    return {
        "gap_id": g.id,
        "employee_reference": g.employee.employee_reference if g.employee else "Staff Member",
        "role_name": g.role.role_name if g.role else "Role",
        "department": g.employee.department if g.employee else "General",
        "required_skill": g.required_skill,
        "gap_level": g.gap_level,
        "current_skills": g.employee.current_skills if g.employee else [],
        "preferred_learning_areas": g.employee.preferred_learning_areas if g.employee else [],
        "accessibility_preferences": g.employee.accessibility_preferences if g.employee else [],
        "recommended_action": g.recommended_action,
        "status": g.status,
    }


@router.post("/analyze")
def run_workforce_analysis(
    business_profile_id: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = verify_business_ownership(db, current_user, business_profile_id)
    result = WorkforceAgent.analyze_workforce_readiness(db, profile.id)
    return result


@router.post("/proposal/{gap_id}")
def create_workforce_proposal(
    gap_id: str,
    business_profile_id: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = verify_business_ownership(db, current_user, business_profile_id)
    try:
        proposal = WorkforceAgent.propose_action_for_skill_gap(db, profile.id, gap_id)
        return {
            "status": "SUCCESS",
            "proposal_id": proposal.id,
            "title": proposal.title,
            "risk_level": proposal.risk_level,
            "message": "Learning ActionProposal created. Human approval required."
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
    result = seed_demo_workforce(db, profile.id)
    return result


@router.delete("/demo/cleanup")
def cleanup_demo_data(
    business_profile_id: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = verify_business_ownership(db, current_user, business_profile_id)
    removed_count = cleanup_demo_workforce(db, profile.id)
    return {"status": "SUCCESS", "removed_count": removed_count}
