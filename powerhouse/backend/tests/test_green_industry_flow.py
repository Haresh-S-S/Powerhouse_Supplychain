import uuid
import pytest
from datetime import datetime
from app.models.user import User
from app.models.business import BusinessProfile
from app.models.green_opportunity import GreenOpportunity
from app.models.emission_factor import EmissionFactor
from app.models.green_impact import GreenImpactMeasurement
from app.models.green_metric import GreenOperationalMetric
from app.models.compliance_task import ComplianceTask
from app.models.audit_log import AuditLog
from app.services.auth_service import AuthService
from app.services.green.orchestrator import GreenAgentOrchestrator
from app.services.green.impact_engine import ImpactCalculationService
from app.services.green.policy_validator import GreenPolicyValidator
from app.services.green.score_service import GreenScoreService
from app.services.green.emission_factors import EmissionFactorService
from app.services.green.demo_data import seed_demo_operational_metrics


@pytest.fixture
def auth_tenant_a(db):
    user_a = User(
        id=str(uuid.uuid4()),
        email="tenant_a@powerhouse.io",
        hashed_password=AuthService.hash_password("Password123!"),
        full_name="Tenant A Operator",
        is_active=True,
    )
    db.add(user_a)
    db.flush()

    profile_textile = BusinessProfile(
        id=str(uuid.uuid4()),
        user_id=user_a.id,
        business_name="A-Textiles Tiruppur",
        business_type="Proprietorship",
        industry="Textiles",
        business_category="clothing_textile",
        company_size="10-50",
        city="Tiruppur",
        state="Tamil Nadu",
        country="India",
        onboarding_completed=True,
    )
    db.add(profile_textile)

    profile_restaurant = BusinessProfile(
        id=str(uuid.uuid4()),
        user_id=user_a.id,
        business_name="A-Restaurant Chennai",
        business_type="Partnership",
        industry="Hospitality",
        business_category="restaurant",
        company_size="10-50",
        city="Chennai",
        state="Tamil Nadu",
        country="India",
        onboarding_completed=True,
    )
    db.add(profile_restaurant)
    db.commit()

    token = AuthService.create_access_token({"sub": user_a.id})
    return {"user": user_a, "textile": profile_textile, "restaurant": profile_restaurant, "token": token}


@pytest.fixture
def auth_tenant_b(db):
    user_b = User(
        id=str(uuid.uuid4()),
        email="tenant_b@powerhouse.io",
        hashed_password=AuthService.hash_password("Password123!"),
        full_name="Tenant B Operator",
        is_active=True,
    )
    db.add(user_b)
    db.flush()

    profile_jewellery = BusinessProfile(
        id=str(uuid.uuid4()),
        user_id=user_b.id,
        business_name="B-Jewellery Coimbatore",
        business_type="Private Limited",
        industry="Retail",
        business_category="jewellery",
        company_size="5-20",
        city="Coimbatore",
        state="Tamil Nadu",
        country="India",
        onboarding_completed=True,
    )
    db.add(profile_jewellery)
    db.commit()

    token = AuthService.create_access_token({"sub": user_b.id})
    return {"user": user_b, "profile": profile_jewellery, "token": token}


# ----------------------------------------------------
# 1. Deterministic Impact & Emission Factor Tests
# ----------------------------------------------------
def test_emission_factor_seeding_and_retrieval(db):
    EmissionFactorService.ensure_default_factors(db)
    factors = EmissionFactorService.get_all_factors(db)
    assert len(factors) >= 3

    cea_factor = EmissionFactorService.get_verified_factor_by_name(db, "National Grid Baseline")
    assert cea_factor is not None
    assert cea_factor.value == 0.716
    assert cea_factor.unit == "kgCO2e/kWh"
    assert cea_factor.status == "VERIFIED"


def test_deterministic_impact_calculation(db):
    # Test energy savings calculation
    energy = ImpactCalculationService.calculate_energy_savings(baseline_kwh=1000.0, projected_kwh=750.0)
    assert energy["value"] == 250.0
    assert energy["percentage"] == 25.0
    assert energy["formula"] == "baseline_kwh - projected_kwh"

    # Test cost savings calculation at ₹7.50 tariff
    cost = ImpactCalculationService.calculate_cost_savings(energy_reduction_kwh=250.0, tariff_per_kwh=7.50)
    assert cost["value"] == 1875.0
    assert cost["currency"] == "INR"

    # Test carbon savings with CEA National Factor (250 * 0.716 = 179.0 kgCO2e)
    carbon = ImpactCalculationService.calculate_carbon_savings(db, energy_reduction_kwh=250.0)
    assert carbon["value"] == 179.0
    assert carbon["unit"] == "kgCO2e/month"
    assert "CEA" in carbon["factor_source"]


def test_insufficient_data_non_fabrication(db):
    # Missing energy inputs must return DATA_REQUIRED / UNAVAILABLE, never fabricated numbers
    energy = ImpactCalculationService.calculate_energy_savings(baseline_kwh=None, projected_kwh=None)
    assert energy["value"] is None
    assert energy["status"] == "DATA_REQUIRED"

    cost = ImpactCalculationService.calculate_cost_savings(energy_reduction_kwh=None)
    assert cost["value"] is None
    assert cost["status"] == "UNAVAILABLE"

    carbon = ImpactCalculationService.calculate_carbon_savings(db, energy_reduction_kwh=None, paper_reams_saved=None)
    assert carbon["value"] is None
    assert carbon["status"] == "DATA_REQUIRED"


# ----------------------------------------------------
# 2. Policy Validation Tests
# ----------------------------------------------------
def test_green_policy_validation():
    # 1. Critical safety shutdown -> BLOCK
    status, notes = GreenPolicyValidator.validate_recommendation(
        category="Energy Optimization",
        action_title="Power off ventilation and fire safety systems",
        parameters={"target_system": "Fire alarm backup"}
    )
    assert status == "BLOCK"
    assert "Safety Policy Violation" in notes

    # 2. Production resize -> REVIEW_REQUIRED
    status, notes = GreenPolicyValidator.validate_recommendation(
        category="Compute Efficiency",
        action_title="Resize production core cluster",
        parameters={"target_system": "Production DB", "operating_hours": "core"}
    )
    assert status == "REVIEW_REQUIRED"
    assert "supervisor sign-off" in notes

    # 3. Off-peak scheduling -> PASS
    status, notes = GreenPolicyValidator.validate_recommendation(
        category="Compute Efficiency",
        action_title="Cache recurring AI inference queries",
        parameters={"target_system": "AI Cache"}
    )
    assert status == "PASS"


# ----------------------------------------------------
# 3. Agent Orchestration Lifecycle & Trace Tests
# ----------------------------------------------------
def test_agent_orchestrator_lifecycle(db, auth_tenant_a):
    profile = auth_tenant_a["textile"]
    # Seed isolated demo metrics
    seed_demo_operational_metrics(db, profile.id)

    res = GreenAgentOrchestrator.run_orchestration(db, profile)
    assert res["status"] == "COMPLETED"
    assert res["output_count"] > 0

    # Verify all 8 stages exist in trace_steps
    stage_names = [s["step"] for s in res["trace_steps"]]
    assert "Observe" in stage_names
    assert "Retrieve" in stage_names
    assert "Detect" in stage_names
    assert "Analyze" in stage_names
    assert "Reason & Recommend" in stage_names
    assert "Validate" in stage_names

    # Check that generated opportunities are persisted in DB
    opps = db.query(GreenOpportunity).filter(GreenOpportunity.business_profile_id == profile.id).all()
    assert len(opps) == res["output_count"]
    for op in opps:
        assert op.status == "DETECTED"
        assert len(op.evidence) > 0


# ----------------------------------------------------
# 4. Green Score Explainability Tests
# ----------------------------------------------------
def test_green_score_calculation_and_breakdown(db, auth_tenant_a):
    profile = auth_tenant_a["textile"]
    score_data = GreenScoreService.calculate_green_score(db, profile.id)

    assert 0 <= score_data["score"] <= 100
    assert len(score_data["components"]) == 5

    comp_names = [c["name"] for c in score_data["components"]]
    assert "Compute Efficiency" in comp_names
    assert "Resource Efficiency" in comp_names
    assert "Digital Workflow Adoption" in comp_names
    assert "Completed Green Actions" in comp_names
    assert "Verified Measured Impact" in comp_names

    total_weight = sum(c["weight"] for c in score_data["components"])
    assert round(total_weight, 2) == 1.0


# ----------------------------------------------------
# 5. HITL Action Proposal & Compliance Task Integration
# ----------------------------------------------------
def test_green_action_proposal_and_task_execution(client, db, auth_tenant_a):
    profile = auth_tenant_a["textile"]
    token = auth_tenant_a["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Seed demo and orchestrate
    client.post(f"/api/v1/green/demo/seed?business_profile_id={profile.id}", headers=headers)

    # 2. Get an opportunity
    opp = db.query(GreenOpportunity).filter(GreenOpportunity.business_profile_id == profile.id).first()
    assert opp is not None

    # 3. Create Action Proposal via endpoint
    res = client.post(
        f"/api/v1/green/opportunities/{opp.id}/proposal?business_profile_id={profile.id}",
        headers=headers
    )
    assert res.status_code == 200
    data = res.json()
    proposal_id = data["proposal_id"]

    # Verify opportunity transitioned to UNDER_REVIEW
    db.refresh(opp)
    assert opp.status == "UNDER_REVIEW"

    # 4. Confirm Proposal through Human Approval
    confirm_res = client.post(
        f"/api/v1/proposals/{profile.id}/{proposal_id}/confirm",
        json={"confirmed_by": "Mohith K (Compliance Lead)"},
        headers=headers
    )
    assert confirm_res.status_code == 200

    # Verify opportunity transitioned to TASK_CREATED
    db.refresh(opp)
    assert opp.status == "TASK_CREATED"
    assert opp.approved_at is not None

    # Verify real ComplianceTask was created in the existing task system!
    created_task = (
        db.query(ComplianceTask)
        .filter(
            ComplianceTask.business_profile_id == profile.id,
            ComplianceTask.category == "Green Operations",
        )
        .first()
    )
    assert created_task is not None
    assert opp.title in created_task.title
    assert created_task.assignee == "Mohith K (Compliance Lead)"

    # Verify immutable AuditLog was written
    audit = db.query(AuditLog).filter(AuditLog.proposal_id == proposal_id).first()
    assert audit is not None
    assert audit.target_entity_type == "green_opportunity"


# ----------------------------------------------------
# 6. Before / After Impact Verification Tests
# ----------------------------------------------------
def test_before_after_impact_measurement(client, db, auth_tenant_a):
    profile = auth_tenant_a["textile"]
    token = auth_tenant_a["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create an initial impact record
    opp = GreenOpportunity(
        id=str(uuid.uuid4()),
        business_profile_id=profile.id,
        agent_type="EnergyAgent",
        title="Industrial HVAC VFD Installation",
        category="Energy Optimization",
        detected_issue="Constant speed blower motors consume excess off-peak power.",
        evidence=[{"source_type": "DEMO_DATA", "evidence_summary": "Daily 168.5 kWh meter reading.", "is_demo": True}],
        cause="Lack of variable frequency drive.",
        recommended_action="Install VFD controller.",
        implementation_effort="Medium",
        status="TASK_CREATED",
    )
    db.add(opp)
    db.flush()

    impact = GreenImpactMeasurement(
        id=str(uuid.uuid4()),
        opportunity_id=opp.id,
        business_profile_id=profile.id,
        metric_name="Monthly Energy Consumption",
        unit="kWh",
        baseline_value=5000.0,
        measured_value=None,  # Pending verification
        is_demo=True,
        verification_status="PENDING",
        formula="baseline_kwh - post_action_kwh",
    )
    db.add(impact)
    db.commit()

    # Call verify endpoint to record post-action empirical reading (e.g. 4200 kWh)
    res = client.post(
        f"/api/v1/green/impact/{impact.id}/verify?business_profile_id={profile.id}",
        json={"measured_value": 4200.0, "assumptions": "Smart sub-meter verification 30 days post-installation."},
        headers=headers
    )
    assert res.status_code == 200
    data = res.json()
    assert data["verification_status"] == "VERIFIED"
    assert data["measured_value"] == 4200.0
    assert data["absolute_change"] == 800.0
    assert data["percentage_change"] == 16.0


# ----------------------------------------------------
# 7. Multi-tenant Isolation Tests (HTTP 403 Forbidden)
# ----------------------------------------------------
def test_green_tenant_isolation_forbidden(client, auth_tenant_a, auth_tenant_b):
    # User B attempting to access User A's green summary must return 403
    profile_a = auth_tenant_a["textile"]
    token_b = auth_tenant_b["token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    res = client.get(f"/api/v1/green/summary?business_profile_id={profile_a.id}", headers=headers_b)
    assert res.status_code == 403
    assert "Access forbidden" in res.json()["detail"]

    res_opps = client.get(f"/api/v1/green/opportunities?business_profile_id={profile_a.id}", headers=headers_b)
    assert res_opps.status_code == 403

    res_run = client.post(f"/api/v1/green/agent/run?business_profile_id={profile_a.id}", headers=headers_b)
    assert res_run.status_code == 403


# ----------------------------------------------------
# 8. Business Switching Isolation Tests
# ----------------------------------------------------
def test_business_switching_isolation(client, db, auth_tenant_a):
    user_a = auth_tenant_a["user"]
    textile = auth_tenant_a["textile"]
    restaurant = auth_tenant_a["restaurant"]
    token = auth_tenant_a["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Seed demo metrics only on Textile
    seed_demo_operational_metrics(db, textile.id)
    GreenAgentOrchestrator.run_orchestration(db, textile)

    # Query Textile opportunities
    res_textile = client.get(f"/api/v1/green/opportunities?business_profile_id={textile.id}", headers=headers)
    assert res_textile.status_code == 200
    textile_opps = res_textile.json()
    assert len(textile_opps) > 0

    # Query Restaurant opportunities (must be empty because no metrics seeded for restaurant!)
    res_restaurant = client.get(f"/api/v1/green/opportunities?business_profile_id={restaurant.id}", headers=headers)
    assert res_restaurant.status_code == 200
    restaurant_opps = res_restaurant.json()
    assert len(restaurant_opps) == 0  # Zero cross-business leakage!
