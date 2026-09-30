import pytest
import uuid
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.core.database import SessionLocal
from app.models.user import User
from app.models.business import BusinessProfile
from app.models.workforce import EmployeeProfile, RoleProfile, SkillGap, LearningPath
from app.models.compliance_task import ComplianceTask
from app.models.audit_log import AuditLog
from app.services.workforce.intelligence_service import WorkforceIntelligenceService
from app.services.workforce.agent import WorkforceAgent
from app.services.workforce.demo_data import seed_demo_workforce, cleanup_demo_workforce
from app.services.proposal_service import ProposalService
from app.services.auth_service import AuthService


@pytest.fixture
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def auth_user_and_profile(db: Session):
    user_id = str(uuid.uuid4())
    user = User(
        id=user_id,
        email=f"workforce_tester_{user_id[:8]}@example.com",
        full_name="HR Director",
        hashed_password="mockhashedpassword"
    )
    db.add(user)
    db.flush()

    profile_id = str(uuid.uuid4())
    profile = BusinessProfile(
        id=profile_id,
        user_id=user.id,
        business_name="Green Fabrications Ltd",
        business_type="Private Limited",
        industry="Manufacturing",
        business_category="manufacturing",
        city="Coimbatore",
        state="Tamil Nadu",
        country="India",
        company_size="Medium",
        employee_count=85,
    )
    db.add(profile)
    db.commit()

    token = AuthService.create_access_token(data={"sub": user.id})
    return {"user": user, "profile": profile, "token": token}


def test_employee_and_role_creation(db: Session, auth_user_and_profile):
    profile = auth_user_and_profile["profile"]

    role = RoleProfile(
        id=str(uuid.uuid4()),
        business_id=profile.id,
        role_name="Quality Assurance Lead",
        department="Operations",
        required_skills=[
            {"skill": "Statistical Process Control", "level": "Advanced"},
            {"skill": "ISO 9001 Auditing", "level": "Intermediate"}
        ],
        optional_skills=["Lean Six Sigma"],
        is_demo=False
    )
    db.add(role)
    db.commit()

    emp = EmployeeProfile(
        id=str(uuid.uuid4()),
        business_id=profile.id,
        employee_reference="EMP-QA-01",
        role="Quality Assurance Lead",
        department="Operations",
        experience_years=3.0,
        current_skills=["ISO 9001 Auditing", "Root Cause Analysis"],
        preferred_learning_areas=["Statistical Process Control"],
        accessibility_preferences=["Captioned Video"],
        is_demo=False
    )
    db.add(emp)
    db.commit()

    saved_role = db.query(RoleProfile).filter(RoleProfile.id == role.id).first()
    assert saved_role is not None
    assert saved_role.role_name == "Quality Assurance Lead"

    saved_emp = db.query(EmployeeProfile).filter(EmployeeProfile.id == emp.id).first()
    assert saved_emp is not None
    assert saved_emp.employee_reference == "EMP-QA-01"


def test_skill_gap_detection_logic(db: Session, auth_user_and_profile):
    profile = auth_user_and_profile["profile"]

    role = RoleProfile(
        id=str(uuid.uuid4()),
        business_id=profile.id,
        role_name="Machinist Level 2",
        department="Manufacturing",
        required_skills=[
            {"skill": "CNC Programming", "level": "Advanced"},
            {"skill": "Machine Guard Safety", "level": "Intermediate"}
        ],
        is_demo=False
    )
    db.add(role)

    emp = EmployeeProfile(
        id=str(uuid.uuid4()),
        business_id=profile.id,
        employee_reference="EMP-M-11",
        role="Machinist Level 2",
        department="Manufacturing",
        experience_years=2.0,
        current_skills=["Machine Guard Safety"],  # Lacks CNC Programming
        accessibility_preferences=["Audio Guides"],
        is_demo=False
    )
    db.add(emp)
    db.commit()

    gaps = WorkforceIntelligenceService.detect_and_sync_skill_gaps(db, profile.id)
    assert len(gaps) >= 1

    cnc_gap = next((g for g in gaps if g.required_skill == "CNC Programming"), None)
    assert cnc_gap is not None
    assert cnc_gap.gap_level in ["High", "Medium"]
    assert "CNC Programming" in cnc_gap.recommended_action


def test_personalized_learning_path_generation(db: Session, auth_user_and_profile):
    profile = auth_user_and_profile["profile"]

    role = RoleProfile(
        id=str(uuid.uuid4()),
        business_id=profile.id,
        role_name="Data Analyst",
        department="Finance",
        required_skills=[{"skill": "Python Pandas", "level": "Intermediate"}],
        is_demo=False
    )
    db.add(role)

    emp = EmployeeProfile(
        id=str(uuid.uuid4()),
        business_id=profile.id,
        employee_reference="EMP-FIN-02",
        role="Data Analyst",
        department="Finance",
        experience_years=1.5,
        current_skills=["Excel"],
        accessibility_preferences=["Screen Reader Compatible"],
        is_demo=False
    )
    db.add(emp)
    db.commit()

    # Detect gaps first
    WorkforceIntelligenceService.detect_and_sync_skill_gaps(db, profile.id)

    # Generate path
    path = WorkforceIntelligenceService.generate_or_sync_learning_path(db, profile.id, emp.id)
    assert path is not None
    assert "Python Pandas" in str(path.skill_sequence)
    assert "Screen Reader Compatible" in str(path.accessibility_accommodations)


def test_workforce_proposal_and_task_execution(db: Session, auth_user_and_profile):
    profile = auth_user_and_profile["profile"]

    role = RoleProfile(
        id=str(uuid.uuid4()),
        business_id=profile.id,
        role_name="ETP Tech",
        department="Safety",
        required_skills=[{"skill": "Effluent Neutralization", "level": "Advanced"}],
        is_demo=False
    )
    db.add(role)

    emp = EmployeeProfile(
        id=str(uuid.uuid4()),
        business_id=profile.id,
        employee_reference="EMP-ENV-09",
        role="ETP Tech",
        department="Safety",
        current_skills=[],
        is_demo=False
    )
    db.add(emp)
    db.flush()

    gap = SkillGap(
        id=str(uuid.uuid4()),
        business_id=profile.id,
        employee_id=emp.id,
        role_id=role.id,
        required_skill="Effluent Neutralization",
        gap_level="High",
        recommended_action="Enroll in Wastewater Treatment Module",
        status="RECOMMENDED"
    )
    db.add(gap)
    db.commit()

    # 1. Propose action
    proposal = WorkforceAgent.propose_action_for_skill_gap(db, profile.id, gap.id)
    assert proposal is not None
    assert proposal.affected_entity_type == "skill_gap"
    assert proposal.status == "Pending Review"

    # 2. Human confirms action
    result = ProposalService.confirm_proposal(db, profile.id, proposal.id, confirmed_by="Mohith K")
    assert result["status"] == "Confirmed"

    # 3. Verify ComplianceTask created under Workforce Intelligence
    task = db.query(ComplianceTask).filter(
        ComplianceTask.business_profile_id == profile.id,
        ComplianceTask.category == "Workforce Intelligence"
    ).first()
    assert task is not None
    assert "Effluent Neutralization" in task.title

    # 4. Verify immutable AuditLog
    audit = db.query(AuditLog).filter(
        AuditLog.business_profile_id == profile.id,
        AuditLog.target_entity_type == "skill_gap"
    ).first()
    assert audit is not None
    assert audit.new_state == "ENROLLED"


def test_workforce_tenant_isolation(db: Session, auth_user_and_profile):
    profile_a = auth_user_and_profile["profile"]
    token_a = auth_user_and_profile["token"]

    user_b_id = str(uuid.uuid4())
    user_b = User(id=user_b_id, email=f"other_hr_{user_b_id[:8]}@example.com", full_name="Other HR", hashed_password="pw")
    db.add(user_b)
    db.flush()

    profile_b = BusinessProfile(
        id=str(uuid.uuid4()),
        user_id=user_b.id,
        business_name="Private Hospital Co",
        business_type="LLP",
        industry="Healthcare",
        city="Bangalore",
        state="Karnataka",
        country="India",
        company_size="Large",
    )
    db.add(profile_b)
    db.commit()

    client = TestClient(app)
    # User A tries to access Profile B's workforce data -> must return 403
    response = client.get(
        f"/api/v1/workforce/summary?business_profile_id={profile_b.id}",
        headers={"Authorization": f"Bearer {token_a}"}
    )
    assert response.status_code == 403


def test_workforce_demo_data_seeding_and_cleanup(db: Session, auth_user_and_profile):
    profile = auth_user_and_profile["profile"]

    # 1. Seed demo data
    res = seed_demo_workforce(db, profile.id)
    assert res["status"] == "SEEDED"
    assert res["roles_seeded"] > 0
    assert res["employees_seeded"] > 0

    demo_emps = db.query(EmployeeProfile).filter(EmployeeProfile.business_id == profile.id, EmployeeProfile.is_demo == True).all()
    assert len(demo_emps) > 0
    for e in demo_emps:
        assert "[DEMO DATA]" in e.employee_reference

    # 2. Cleanup demo data
    removed = cleanup_demo_workforce(db, profile.id)
    assert removed > 0

    remaining = db.query(EmployeeProfile).filter(EmployeeProfile.business_id == profile.id, EmployeeProfile.is_demo == True).all()
    assert len(remaining) == 0


def test_get_roles_endpoint_and_business_categories(db: Session, auth_user_and_profile):
    profile = auth_user_and_profile["profile"]
    token = auth_user_and_profile["token"]
    client = TestClient(app)

    # 1. Test unauthenticated request fails
    unauth_res = client.get(f"/api/v1/workforce/roles?business_profile_id={profile.id}")
    assert unauth_res.status_code == 401

    # 2. Seed restaurant demo data
    profile.business_category = "restaurant"
    db.commit()
    seed_demo_workforce(db, profile.id)

    res = client.get(
        f"/api/v1/workforce/roles?business_profile_id={profile.id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 200
    roles = res.json()
    assert len(roles) >= 2
    assert any("Food Safety" in r["role_name"] for r in roles)
    for r in roles:
        assert "role_name" in r
        assert "department" in r
        assert "criticality" in r
        assert "required_skills" in r
        assert "optional_skills" in r
        assert r["is_demo"] is True

    # 3. Switch to Retail category
    profile.business_category = "retail"
    db.commit()
    seed_demo_workforce(db, profile.id)

    res_retail = client.get(
        f"/api/v1/workforce/roles?business_profile_id={profile.id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res_retail.status_code == 200
    retail_roles = res_retail.json()
    assert any("Store Operations" in r["role_name"] or "Inventory" in r["role_name"] for r in retail_roles)

    # 4. Cleanup
    cleanup_demo_workforce(db, profile.id)
