import pytest
import uuid
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.core.database import SessionLocal, engine, Base
from app.models.user import User
from app.models.business import BusinessProfile
from app.services.auth_service import AuthService
from app.supply_chain_ai.adapters.distilbert_risk_adapter import DistilBertRiskAdapter
from app.supply_chain_ai.adapters.hredd_adapter import HreddRiskAdapter
from app.supply_chain_ai.adapters.inventory_fusion_adapter import InventoryFusionAdapter
from app.supply_chain_ai.adapters.supplymind_adapter import SupplyMindAdapter
from app.supply_chain_ai.adapters.ortools_routing_adapter import OrToolsRoutingAdapter
from app.supply_chain_ai.adapters.qwen_adapter import QwenSupplyChainAdapter


@pytest.fixture(scope="module")
def db_session():
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="module")
def auth_headers(db_session: Session):
    user_id = str(uuid.uuid4())
    user = User(
        id=user_id,
        email=f"tower_tester_{user_id[:8]}@example.com",
        full_name="Tower Controller",
        hashed_password="mockhashedpassword"
    )
    db_session.add(user)
    db_session.flush()

    profile_id = str(uuid.uuid4())
    profile = BusinessProfile(
        id=profile_id,
        user_id=user.id,
        business_name="Powerhouse Tower Logistics",
        business_type="Private Limited",
        industry="Automotive & Electronics",
        business_category="manufacturing",
        city="Stuttgart",
        state="Baden-Württemberg",
        country="Germany",
        company_size="Enterprise",
        employee_count=500,
    )
    db_session.add(profile)
    db_session.commit()

    token = AuthService.create_access_token(data={"sub": user.id})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


def test_ai_adapters_availability():
    """Verify that all local AI adapters load properly and run predictions."""
    # 1. DistilBERT Risk Adapter
    risk_adapter = DistilBertRiskAdapter.get()
    risk_res = risk_adapter.classify_text("Supplier experiencing major delivery delays and component quality defects")
    assert "risk_level" in risk_res
    assert risk_res["risk_level"] in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    assert "confidence" in risk_res

    # 2. HREDD Adapter
    hredd_adapter = HreddRiskAdapter.get()
    hredd_res = hredd_adapter.predict_adverse_signals("Audit revealed forced overtime and excessive factory hours")
    assert "all_categories" in hredd_res
    assert "esg_risk_score" in hredd_res

    # 3. Inventory Fusion Adapter
    fusion_adapter = InventoryFusionAdapter.get()
    fc_res = fusion_adapter.forecast_demand(
        sku="SKU-100",
        history_values=[120.0, 130.0, 125.0, 140.0, 135.0, 150.0],
        horizon_days=14,
    )
    assert len(fc_res["points"]) == 14
    assert "p10" in fc_res["points"][0]
    assert "p50" in fc_res["points"][0]
    assert "p90" in fc_res["points"][0]

    # 4. SupplyMind Adapter
    sm_adapter = SupplyMindAdapter.get()
    sm_res = sm_adapter.get_calibrated_impact_curve(
        disruption_id="SIG-TYPHOON-GAEMI",
        severity=0.85,
    )
    assert "timeline" in sm_res
    assert "quantitative_summary" in sm_res
    assert len(sm_res["timeline"]) > 0

    # 5. OR-Tools Adapter
    ortools_adapter = OrToolsRoutingAdapter.get()
    route_res = ortools_adapter.optimize_route(
        origin="Rotterdam Port",
        destination="Munich DC",
        disrupted_nodes=["Frankfurt Hub"],
        available_nodes=["Rotterdam Port", "Antwerp Port", "Cologne Depot", "Stuttgart Hub", "Munich DC"],
        cost_multiplier=1.1
    )
    assert "optimized_path" in route_res
    assert "total_distance_km" in route_res
    assert "Frankfurt Hub" not in route_res["optimized_path"]

    # 6. Qwen / Deterministic Explainability
    qwen_ad = QwenSupplyChainAdapter.get()
    why_dict = qwen_ad.explain_recommendation(
        title="Reroute Shipments via Antwerp",
        recommendation_type="reroute",
        metrics={"cost_change_pct": 8.5, "delay_change_days": -4, "risk_reduction_pct": 32.0},
        context="Rotterdam port congestion has delayed sea freight by 10 days."
    )
    assert "why_factors" in why_dict
    assert len(why_dict["why_factors"]) > 0
    assert len(why_dict["executive_summary"]) > 20


def test_control_tower_seed_and_dashboard(client, auth_headers):
    """Test seeding demo data and fetching control tower dashboard summary."""
    # Seed demo data
    seed_res = client.post("/api/v1/supply-chain/tower/demo/seed", headers=auth_headers)
    assert seed_res.status_code == 200
    data = seed_res.json()
    assert data["status"] == "success"
    assert data["suppliers"] > 0
    assert data["routes"] > 0

    # Fetch dashboard summary
    dash_res = client.get("/api/v1/supply-chain/tower/dashboard", headers=auth_headers)
    assert dash_res.status_code == 200
    dash_data = dash_res.json()
    assert "kpis" in dash_data
    assert "overall_resilience" in dash_data["kpis"]
    assert "supplier_risk" in dash_data["kpis"]
    assert "inventory_risk" in dash_data["kpis"]
    assert "active_disruptions" in dash_data["kpis"]
    assert len(dash_data["disruptions"]) > 0
    assert len(dash_data["pending_approvals"]) > 0


def test_control_tower_network_topology(client, auth_headers):
    """Test fetching interactive network topology nodes and edges."""
    res = client.get("/api/v1/supply-chain/tower/network", headers=auth_headers)
    assert res.status_code == 200
    net_data = res.json()
    assert "nodes" in net_data
    assert "edges" in net_data
    assert len(net_data["nodes"]) >= 10
    assert len(net_data["edges"]) >= 8

    # Verify node types exist
    node_types = {n["type"] for n in net_data["nodes"]}
    assert "supplier" in node_types
    assert "port" in node_types
    assert "warehouse" in node_types
    assert "factory" in node_types


def test_supplier_risk_and_radar(client, auth_headers):
    """Test supplier list and 8-dimensional radar chart calculation."""
    # List suppliers
    sup_res = client.get("/api/v1/supply-chain/tower/suppliers", headers=auth_headers)
    assert sup_res.status_code == 200
    suppliers = sup_res.json()
    assert len(suppliers) > 0

    target_id = suppliers[0]["id"]
    radar_res = client.get(f"/api/v1/supply-chain/tower/supplier/{target_id}/radar", headers=auth_headers)
    assert radar_res.status_code == 200
    radar_data = radar_res.json()
    assert "dimensions" in radar_data
    assert len(radar_data["dimensions"]) == 8
    dim_names = [d["dimension"] for d in radar_data["dimensions"]]
    assert "Reliability" in dim_names
    assert "ESG Risk" in dim_names
    assert "Geopolitical Risk" in dim_names
    assert "ai_risk_score" in radar_data


def test_demand_forecast_endpoint(client, auth_headers):
    """Test demand forecast endpoint with p10, p50, p90 confidence bounds."""
    res = client.post("/api/v1/supply-chain/tower/forecast", headers=auth_headers, json={
        "product_id": "SKU-AUTO-01",
        "horizon_days": 30
    })
    assert res.status_code == 200
    fc = res.json()
    assert fc["product_id"] == "SKU-AUTO-01"
    assert len(fc["points"]) == 30
    assert "predicted_change_pct" in fc


def test_scenario_simulation(client, auth_headers):
    """Test simulation of port closure scenario comparing Baseline, Disrupted, and AI Response."""
    res = client.post("/api/v1/supply-chain/tower/scenario/simulate", headers=auth_headers, json={
        "scenario_type": "port_closure",
        "title": "Rotterdam Deep-Sea Berth Strike",
        "duration_days": 10,
        "affected_nodes": ["PORT-ROTTERDAM"],
        "cost_increase_pct": 18.0
    })
    assert res.status_code == 200
    sim = res.json()
    assert "comparison" in sim
    assert "disrupted_metrics" in sim
    assert "ai_response_metrics" in sim
    assert sim["disrupted_metrics"]["delay_days"] > 0
    assert sim["ai_response_metrics"]["delay_days"] < sim["disrupted_metrics"]["delay_days"]
    assert "ai_summary" in sim


def test_logistics_reroute_optimization(client, auth_headers):
    """Test OR-Tools route bypass generation."""
    res = client.post("/api/v1/supply-chain/tower/route/optimize", headers=auth_headers, json={
        "route_id": "ROUTE-01",
        "avoid_nodes": ["PORT-ROTTERDAM"]
    })
    assert res.status_code == 200
    opt = res.json()
    assert "comparison" in opt
    assert "optimized_reroute" in opt
    assert opt["comparison"]["cost_increase_pct"] >= 0


def test_human_approval_gate_and_audit(client, auth_headers):
    """Test human approval gate decision (approve/reject) and audit trail verification."""
    # List pending recommendations
    recs_res = client.get("/api/v1/supply-chain/tower/approvals", headers=auth_headers)
    assert recs_res.status_code == 200
    recs = recs_res.json()
    assert len(recs) > 0

    rec_id = recs[0]["id"]
    dec_res = client.post("/api/v1/supply-chain/tower/approval/decision", headers=auth_headers, json={
        "recommendation_id": rec_id,
        "decision": "approved",
        "decision_notes": "Authorized by Supply Chain Director for immediate rerouting."
    })
    assert dec_res.status_code == 200
    dec_data = dec_res.json()
    assert dec_data["status"] == "APPROVED"

    # Verify audit trail has recorded the human decision
    audit_res = client.get("/api/v1/supply-chain/tower/audit", headers=auth_headers)
    assert audit_res.status_code == 200
    logs = audit_res.json()
    assert any("Human Approved" in log["action"] or log.get("decision") == "APPROVED" for log in logs)


def test_agent_chat_assistant(client, auth_headers):
    """Test Qwen3 + smolagents AI assistant endpoint."""
    res = client.post("/api/v1/supply-chain/tower/agent/chat", headers=auth_headers, json={
        "prompt": "Which suppliers are most vulnerable right now?",
        "context": {}
    })
    assert res.status_code == 200
    chat_data = res.json()
    assert "answer" in chat_data or "response" in chat_data
    answer_text = chat_data.get("answer") or chat_data.get("response")
    assert len(answer_text) > 30
    assert "agent" in chat_data
