import pytest
import uuid
from datetime import datetime
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.core.database import SessionLocal
from app.models.user import User
from app.models.business import BusinessProfile
from app.models.supplier import Supplier, SupplierDocument, SupplyItem, SupplyChainRisk
from app.models.compliance_task import ComplianceTask
from app.models.audit_log import AuditLog
from app.services.supply_chain.risk_service import SupplyChainRiskService
from app.services.supply_chain.agent import SupplyChainAgent
from app.services.supply_chain.demo_data import seed_demo_supply_chain, cleanup_demo_supply_chain
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
        email=f"supply_tester_{user_id[:8]}@example.com",
        full_name="Supply Chain Manager",
        hashed_password="mockhashedpassword"
    )
    db.add(user)
    db.flush()

    profile_id = str(uuid.uuid4())
    profile = BusinessProfile(
        id=profile_id,
        user_id=user.id,
        business_name="Testile Dynamics Ltd",
        business_type="Private Limited",
        industry="Textiles",
        business_category="clothing_textile",
        city="Tiruppur",
        state="Tamil Nadu",
        country="India",
        company_size="Medium",
        employee_count=120,
    )
    db.add(profile)
    db.commit()

    token = AuthService.create_access_token(data={"sub": user.id})
    return {"user": user, "profile": profile, "token": token}


def test_supplier_and_item_creation(db: Session, auth_user_and_profile):
    profile = auth_user_and_profile["profile"]

    sup = Supplier(
        id=str(uuid.uuid4()),
        business_id=profile.id,
        name="Apex Yarns Pvt Ltd",
        supplier_type="Raw Material",
        location="Erode, Tamil Nadu",
        country="India",
        products_or_materials=["Organic Cotton 30s"],
        dependency_percentage=85.0,
        lead_time_days=10,
        status="Active",
        risk_status="High",
        is_demo=False
    )
    db.add(sup)
    db.commit()

    item = SupplyItem(
        id=str(uuid.uuid4()),
        business_id=profile.id,
        name="Organic Cotton Yarn 30s",
        category="Raw Material",
        criticality="Critical",
        primary_supplier_id=sup.id,
        alternate_supplier_count=0,
        dependency_percentage=85.0,
        buffer_stock_days=5,
        is_demo=False
    )
    db.add(item)
    db.commit()

    saved_sup = db.query(Supplier).filter(Supplier.id == sup.id).first()
    assert saved_sup is not None
    assert saved_sup.name == "Apex Yarns Pvt Ltd"

    saved_item = db.query(SupplyItem).filter(SupplyItem.id == item.id).first()
    assert saved_item is not None
    assert saved_item.primary_supplier_id == sup.id


def test_single_supplier_dependency_risk_detection(db: Session, auth_user_and_profile):
    profile = auth_user_and_profile["profile"]

    sup = Supplier(
        id=str(uuid.uuid4()),
        business_id=profile.id,
        name="Sole Source Chem",
        supplier_type="Chemicals",
        location="Surat",
        country="India",
        products_or_materials=["Catalyst X"],
        dependency_percentage=90.0,
        lead_time_days=14,
        status="Active",
    )
    db.add(sup)
    db.flush()

    item = SupplyItem(
        id=str(uuid.uuid4()),
        business_id=profile.id,
        name="Critical Dye Catalyst X",
        category="Raw Material",
        criticality="Critical",
        primary_supplier_id=sup.id,
        alternate_supplier_count=0,
        dependency_percentage=90.0,
        buffer_stock_days=4,
    )
    db.add(item)
    db.commit()

    risks = SupplyChainRiskService.detect_and_sync_risks(db, profile.id)
    assert len(risks) >= 1

    single_source_risk = next((r for r in risks if r.category == "Single Supplier Dependency"), None)
    assert single_source_risk is not None
    assert "Critical Dye Catalyst X" in single_source_risk.title
    assert single_source_risk.priority == "Critical"
    assert single_source_risk.policy_check_status == "PASS"


def test_missing_supplier_documents_detection(db: Session, auth_user_and_profile):
    profile = auth_user_and_profile["profile"]

    sup = Supplier(
        id=str(uuid.uuid4()),
        business_id=profile.id,
        name="Unverified Logistics Hub",
        supplier_type="Logistics",
        location="Chennai",
        country="India",
        products_or_materials=["Freight"],
        lead_time_days=7,
        status="Active",
    )
    db.add(sup)
    db.flush()

    doc = SupplierDocument(
        id=str(uuid.uuid4()),
        supplier_id=sup.id,
        document_name="ISO 9001 Certificate",
        document_type="ISO 9001",
        verification_status="Expired",
        expiry_date="2025-12-31"
    )
    db.add(doc)
    db.commit()

    risks = SupplyChainRiskService.detect_and_sync_risks(db, profile.id)
    doc_risk = next((r for r in risks if r.category == "Missing Documentation"), None)
    assert doc_risk is not None
    assert "Unverified Logistics Hub" in doc_risk.title


def test_resilience_score_calculation(db: Session, auth_user_and_profile):
    profile = auth_user_and_profile["profile"]
    score_data = SupplyChainRiskService.calculate_resilience_score(db, profile.id)
    assert "score" in score_data
    assert "rating" in score_data
    assert 10 <= score_data["score"] <= 100


def test_supply_chain_proposal_and_task_execution(db: Session, auth_user_and_profile):
    profile = auth_user_and_profile["profile"]

    risk = SupplyChainRisk(
        id=str(uuid.uuid4()),
        business_id=profile.id,
        title="Mitigate Single Source Yarn Vendor",
        category="Single Supplier Dependency",
        priority="High",
        severity="Critical",
        evidence={"item": "Cotton 40s"},
        issue="85% reliance on single mill",
        cause="No secondary qualified",
        recommended_action="Qualify secondary spinning mill in Erode",
        status="RECOMMENDED",
        policy_check_status="PASS"
    )
    db.add(risk)
    db.commit()

    # 1. Propose action
    proposal = SupplyChainAgent.propose_action_for_risk(db, profile.id, risk.id)
    assert proposal is not None
    assert proposal.status == "Pending Review"
    assert proposal.affected_entity_type == "supply_chain_risk"

    # 2. Human confirms action
    result = ProposalService.confirm_proposal(db, profile.id, proposal.id, confirmed_by="Mohith K")
    assert result["status"] == "Confirmed"

    # 3. Verify ComplianceTask created
    task = db.query(ComplianceTask).filter(
        ComplianceTask.business_profile_id == profile.id,
        ComplianceTask.category == "Supply Chain Resilience"
    ).first()
    assert task is not None
    assert "Mitigate Single Source Yarn Vendor" in task.title

    # 4. Verify immutable AuditLog
    audit = db.query(AuditLog).filter(
        AuditLog.business_profile_id == profile.id,
        AuditLog.target_entity_type == "supply_chain_risk"
    ).first()
    assert audit is not None
    assert audit.new_state == "ACTION_CREATED"


def test_supply_chain_tenant_isolation(db: Session, auth_user_and_profile):
    profile_a = auth_user_and_profile["profile"]
    token_a = auth_user_and_profile["token"]

    # Profile B belonging to different user
    user_b_id = str(uuid.uuid4())
    user_b = User(id=user_b_id, email=f"other_supply_{user_b_id[:8]}@example.com", full_name="Other User", hashed_password="pw")
    db.add(user_b)
    db.flush()

    profile_b = BusinessProfile(
        id=str(uuid.uuid4()),
        user_id=user_b.id,
        business_name="Competitor Retailers",
        business_type="LLP",
        industry="Retail",
        city="Mumbai",
        state="Maharashtra",
        country="India",
        company_size="Small",
    )
    db.add(profile_b)
    db.commit()

    client = TestClient(app)
    # User A tries to access Profile B's supply chain summary -> must return 403
    response = client.get(
        f"/api/v1/supply-chain/summary?business_profile_id={profile_b.id}",
        headers={"Authorization": f"Bearer {token_a}"}
    )
    assert response.status_code == 403


def test_supply_chain_demo_data_seeding_and_cleanup(db: Session, auth_user_and_profile):
    profile = auth_user_and_profile["profile"]

    # 1. Seed demo data
    res = seed_demo_supply_chain(db, profile.id)
    assert res["status"] == "SEEDED"
    assert res["suppliers_seeded"] > 0
    assert res["items_seeded"] > 0

    demo_sups = db.query(Supplier).filter(Supplier.business_id == profile.id, Supplier.is_demo == True).all()
    assert len(demo_sups) > 0
    for s in demo_sups:
        assert "[DEMO DATA]" in s.name

    # 2. Cleanup demo data
    removed = cleanup_demo_supply_chain(db, profile.id)
    assert removed > 0

    remaining_demo = db.query(Supplier).filter(Supplier.business_id == profile.id, Supplier.is_demo == True).all()
    assert len(remaining_demo) == 0
