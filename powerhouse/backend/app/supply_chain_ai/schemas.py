"""
Supply Chain AI Pydantic Schemas
--------------------------------
Type definitions for all Control Tower API endpoints.
Flexible and robust to support various client and test payload signatures.
"""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, root_validator


class DisruptionAnalysisRequest(BaseModel):
    business_id: Optional[str] = None
    signal_id: Optional[str] = "SIG-TYPHOON-GAEMI"
    severity: Optional[float] = 0.85
    event_type: Optional[str] = None
    affected_nodes: Optional[List[str]] = None


class ForecastRequest(BaseModel):
    business_id: Optional[str] = None
    sku: Optional[str] = None
    product_id: Optional[str] = None
    warehouse_id: Optional[str] = None
    horizon_days: Optional[int] = 30

    @root_validator(pre=True)
    def harmonize_sku(cls, values):
        if not values.get("sku") and values.get("product_id"):
            values["sku"] = values.get("product_id")
        elif not values.get("sku"):
            values["sku"] = "SKU-DRAM-001"
        return values


class ScenarioSimulationRequest(BaseModel):
    business_id: Optional[str] = None
    scenario_type: str = "port_closure"
    title: Optional[str] = None
    name: Optional[str] = None
    duration_days: Optional[int] = None
    affected_nodes: Optional[List[str]] = None
    cost_increase_pct: Optional[float] = None
    parameters: Dict[str, Any] = Field(default_factory=dict)

    @root_validator(pre=True)
    def pack_extra_params(cls, values):
        params = values.get("parameters") or {}
        if "duration_days" in values and "duration_days" not in params:
            params["duration_days"] = values["duration_days"]
        if "affected_nodes" in values and "affected_nodes" not in params:
            params["affected_nodes"] = values["affected_nodes"]
        if "cost_increase_pct" in values and "cost_increase_pct" not in params:
            params["cost_increase_pct"] = values["cost_increase_pct"]
        if "title" in values and not values.get("name"):
            values["name"] = values["title"]
        values["parameters"] = params
        return values


class RouteOptimizationRequest(BaseModel):
    business_id: Optional[str] = None
    route_id: Optional[str] = None
    origin: Optional[str] = "Taiwan Strait (TSMC Hsinchu)"
    destination: Optional[str] = "DC South (Dallas Regional)"
    blocked_node: Optional[str] = "Port of Kaohsiung"
    avoid_nodes: Optional[List[str]] = None

    @root_validator(pre=True)
    def harmonize_blocked(cls, values):
        avoid = values.get("avoid_nodes")
        if avoid and len(avoid) > 0 and not values.get("blocked_node"):
            values["blocked_node"] = avoid[0]
        return values


class RebalanceRequest(BaseModel):
    business_id: Optional[str] = None
    sku: Optional[str] = "SKU-DRAM-001"
    source_warehouse: Optional[str] = "DC North (Hamburg)"
    target_warehouse: Optional[str] = "DC South (Dallas)"


class ApprovalDecisionRequest(BaseModel):
    business_id: Optional[str] = None
    recommendation_id: str
    decision: str  # "APPROVED" or "REJECTED" (case-insensitive)
    decided_by: Optional[str] = "Supply Chain Operations Lead"
    rejection_reason: Optional[str] = None
    decision_notes: Optional[str] = None

    @root_validator(pre=True)
    def harmonize_notes(cls, values):
        dec = values.get("decision", "").upper()
        values["decision"] = dec
        notes = values.get("decision_notes")
        if notes and not values.get("rejection_reason"):
            values["rejection_reason"] = notes
        return values


class AgentChatRequest(BaseModel):
    business_id: Optional[str] = None
    query: Optional[str] = None
    prompt: Optional[str] = None
    context: Optional[Dict[str, Any]] = Field(default_factory=dict)
    conversation_history: Optional[List[Dict[str, str]]] = Field(default_factory=list)

    @root_validator(pre=True)
    def harmonize_prompt(cls, values):
        if not values.get("query") and values.get("prompt"):
            values["query"] = values.get("prompt")
        elif not values.get("query"):
            values["query"] = "What is the status of the supply chain?"
        return values


class SeedDemoRequest(BaseModel):
    business_id: Optional[str] = None
