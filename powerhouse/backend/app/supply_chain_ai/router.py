"""
Supply Chain Control Tower API Router
-------------------------------------
Prefix: /supply-chain/tower
Integrates all Resilient Supply Chain endpoints without modifying
any existing compliance, workforce, green, or auth routes.
"""
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status as http_status
from sqlalchemy.orm import Session

from app.dependencies.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.models.business import BusinessProfile

from app.supply_chain_ai.config import check_ai_assets_status
from app.supply_chain_ai.schemas import (
    DisruptionAnalysisRequest,
    ForecastRequest,
    ScenarioSimulationRequest,
    RouteOptimizationRequest,
    RebalanceRequest,
    ApprovalDecisionRequest,
    AgentChatRequest,
    SeedDemoRequest,
)
from app.supply_chain_ai.services.control_tower_service import ControlTowerService
from app.supply_chain_ai.services.disruption_service import DisruptionService
from app.supply_chain_ai.services.inventory_service import InventoryIntelligenceService
from app.supply_chain_ai.services.supplier_risk_service import SupplierRiskService
from app.supply_chain_ai.services.scenario_service import ScenarioPlanningService
from app.supply_chain_ai.services.logistics_service import LogisticsService
from app.supply_chain_ai.services.approval_service import HumanApprovalService
from app.supply_chain_ai.services.demo_seed_service import (
    seed_resilient_control_tower_data,
    cleanup_control_tower_demo_data,
)
from app.supply_chain_ai.adapters.qwen_adapter import QwenSupplyChainAdapter
from app.supply_chain_ai.adapters.smolagents_orchestrator import SmolagentsSupplyChainOrchestrator

router = APIRouter(prefix="/supply-chain/tower", tags=["Resilient Supply Chain Control Tower"])


def resolve_business_id(db: Session, business_id: Optional[str], current_user: User) -> str:
    """Find or create an active business profile ID for the current user."""
    if business_id:
        profile = db.query(BusinessProfile).filter(BusinessProfile.id == business_id).first()
        if not profile:
            profile = BusinessProfile(
                id=business_id,
                user_id=current_user.id,
                business_name="Powerhouse Tower Logistics",
                business_type="Enterprise",
                industry="Automotive & Electronics",
                business_category="manufacturing",
            )
            db.add(profile)
            db.commit()
        return business_id

    # Fallback to existing profile of user
    profile = db.query(BusinessProfile).filter(BusinessProfile.user_id == current_user.id).first()
    if profile:
        return profile.id

    # Create default
    default_id = f"biz-{current_user.id[:8]}"
    profile = BusinessProfile(
        id=default_id,
        user_id=current_user.id,
        business_name="Powerhouse Tower Logistics",
        business_type="Enterprise",
        industry="Automotive & Electronics",
        business_category="manufacturing",
    )
    db.add(profile)
    db.commit()
    return default_id


# 1. AI Stack Status
@router.get("/ai-status")
def get_ai_status():
    return check_ai_assets_status()


# 2. Control Tower Dashboard & Top KPIs
@router.get("/dashboard")
def get_control_tower_dashboard(
    business_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    bid = resolve_business_id(db, business_id, current_user)
    return ControlTowerService.get_dashboard_summary(db, bid)


# 3. Supply Network Topology Graph
@router.get("/network")
def get_network_topology(
    business_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    bid = resolve_business_id(db, business_id, current_user)
    return ControlTowerService.get_network_topology(db, bid)


# 4. Suppliers & Ranked Table
@router.get("/suppliers")
def get_suppliers(
    business_id: Optional[str] = Query(None),
    risk_filter: str = Query("ALL"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    bid = resolve_business_id(db, business_id, current_user)
    return SupplierRiskService.get_suppliers_with_risk(db, bid, risk_filter)


# 5. Supplier Spider / Radar Chart
@router.get("/supplier/{supplier_id}/radar")
def get_supplier_radar(
    supplier_id: str,
    business_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    bid = resolve_business_id(db, business_id, current_user)
    return SupplierRiskService.get_supplier_radar_profile(db, supplier_id)


# 6. Inventory Health Matrix & Heatmap
@router.get("/inventory")
def get_inventory_matrix(
    business_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    bid = resolve_business_id(db, business_id, current_user)
    return InventoryIntelligenceService.get_inventory_health_matrix(db, bid)


# 7. Demand Forecasting (Inventory Fusion)
@router.post("/forecast")
def forecast_demand(
    req: ForecastRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    bid = resolve_business_id(db, req.business_id, current_user)
    return InventoryIntelligenceService.forecast_sku_demand(
        sku=req.sku or "SKU-DRAM-001",
        warehouse_id=req.warehouse_id,
        horizon_days=req.horizon_days or 30,
    )


# 8. Live Disruption Feed
@router.get("/disruptions")
def get_disruptions(
    business_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    bid = resolve_business_id(db, business_id, current_user)
    return DisruptionService.get_live_disruptions(db, bid)


# 9. Disruption Impact Curve (SupplyMind)
@router.post("/disruption/analyze")
def analyze_disruption(
    req: DisruptionAnalysisRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    bid = resolve_business_id(db, req.business_id, current_user)
    return DisruptionService.get_disruption_impact_curve(
        disruption_id=req.signal_id or "SIG-TYPHOON-GAEMI",
        severity=req.severity or 0.85,
    )


# 10. Scenarios List
@router.get("/scenarios")
def get_scenarios(
    business_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    bid = resolve_business_id(db, business_id, current_user)
    return ScenarioPlanningService.get_available_scenarios(db, bid)


# 11. Run Scenario Simulation
@router.post("/scenario/simulate")
def simulate_scenario(
    req: ScenarioSimulationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    bid = resolve_business_id(db, req.business_id, current_user)
    return ScenarioPlanningService.simulate_scenario(
        db=db,
        business_id=bid,
        scenario_type=req.scenario_type,
        parameters=req.parameters,
        name=req.name or req.title,
    )


# 12. Routes List & Optimization (OR-Tools)
@router.get("/routes")
def get_routes(
    business_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    bid = resolve_business_id(db, business_id, current_user)
    return LogisticsService.get_routes(db, bid)


@router.post("/route/optimize")
def optimize_route(
    req: RouteOptimizationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    bid = resolve_business_id(db, req.business_id, current_user)
    return LogisticsService.get_route_comparison(
        origin=req.origin or "Taiwan Strait (TSMC Hsinchu)",
        destination=req.destination or "DC South (Dallas Regional)",
        blocked_node=req.blocked_node or "Port of Kaohsiung",
    )


# 13. Inventory Rebalancing Recommendation
@router.post("/inventory/rebalance")
def rebalance_inventory(
    req: RebalanceRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    bid = resolve_business_id(db, req.business_id, current_user)
    return InventoryIntelligenceService.generate_rebalancing_recommendation(
        sku=req.sku or "SKU-DRAM-001",
        source_warehouse=req.source_warehouse or "DC North (Hamburg)",
        target_warehouse=req.target_warehouse or "DC South (Dallas)",
    )


# 14. Human-in-the-Loop Approvals
@router.get("/approvals")
def get_approvals(
    business_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    bid = resolve_business_id(db, business_id, current_user)
    return HumanApprovalService.get_pending_recommendations(db, bid)


@router.post("/approval/decision")
def make_approval_decision(
    req: ApprovalDecisionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    bid = resolve_business_id(db, req.business_id, current_user)
    try:
        return HumanApprovalService.process_decision(
            db=db,
            business_id=bid,
            recommendation_id=req.recommendation_id,
            decision=req.decision,
            decided_by=req.decided_by or "Supply Chain Operations Lead",
            rejection_reason=req.rejection_reason,
        )
    except ValueError as e:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail=str(e))


# 15. Compliance & Agent Decision Audit Trail
@router.get("/audit")
def get_audit_trail(
    business_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    bid = resolve_business_id(db, business_id, current_user)
    return HumanApprovalService.get_audit_trail(db, bid)


# 16. Natural Language Assistant Chat (Qwen3 + smolagents)
@router.post("/agent/chat")
def supply_chain_chat(
    req: AgentChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    bid = resolve_business_id(db, req.business_id, current_user)
    qwen = QwenSupplyChainAdapter.get()
    return qwen.answer_assistant_query(
        query=req.query or req.prompt,
        context={
            "business_id": bid,
            **(req.context or {}),
        },
    )


# 17. smolagents Autonomous Investigation Workflow Trigger
@router.post("/agent/run-investigation")
def run_agent_investigation(
    req: DisruptionAnalysisRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    bid = resolve_business_id(db, req.business_id, current_user)
    orchestrator = SmolagentsSupplyChainOrchestrator.get()
    return orchestrator.run_investigation_workflow(
        trigger_event=req.signal_id or "Port of Kaohsiung Typhoon Closure",
        affected_sku="SKU-DRAM-001",
    )


# 18. Demo Data Seeding & Cleanup
@router.post("/demo/seed")
def seed_demo(
    req: Optional[SeedDemoRequest] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    req_bid = req.business_id if req else None
    bid = resolve_business_id(db, req_bid, current_user)
    return seed_resilient_control_tower_data(db, bid)


@router.delete("/demo/cleanup")
def cleanup_demo(
    business_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    bid = resolve_business_id(db, business_id, current_user)
    cleanup_control_tower_demo_data(db, bid)
    return {"status": "success", "message": "Demo control tower data removed."}
