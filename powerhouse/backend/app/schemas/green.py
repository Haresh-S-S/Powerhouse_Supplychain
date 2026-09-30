from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


# ----------------------------------------------------
# 1. Operational Metric Schemas
# ----------------------------------------------------
class GreenMetricCreate(BaseModel):
    business_profile_id: str
    metric_type: str
    value: float
    unit: str
    is_demo: bool = False
    label: Optional[str] = None


class GreenMetricResponse(BaseModel):
    id: str
    business_profile_id: str
    metric_type: str
    value: float
    unit: str
    is_demo: bool
    label: Optional[str] = None
    collected_at: datetime

    class Config:
        from_attributes = True


# ----------------------------------------------------
# 2. Emission Factor Schemas
# ----------------------------------------------------
class EmissionFactorResponse(BaseModel):
    id: str
    name: str
    value: float
    unit: str
    source: str
    source_version: Optional[str] = None
    geography: str
    scope: str
    effective_date: Optional[str] = None
    review_date: Optional[str] = None
    status: str

    class Config:
        from_attributes = True


# ----------------------------------------------------
# 3. Opportunity Schemas
# ----------------------------------------------------
class OpportunityEvidenceItem(BaseModel):
    source_type: str  # BUSINESS_PROFILE, DOCUMENT, TASK, REPORT, ENERGY_DATA, COMPUTE_DATA, SYSTEM_METRIC, DEMO_DATA
    source_id: Optional[str] = None
    source_field: Optional[str] = None
    observation_time: Optional[str] = None
    metric: Optional[str] = None
    value: Optional[Any] = None
    evidence_summary: str
    is_demo: bool = False


class GreenOpportunityResponse(BaseModel):
    id: str
    business_profile_id: str
    agent_type: str
    title: str
    category: str
    priority: str
    severity: str
    detected_issue: str
    evidence: List[Dict[str, Any]]
    cause: str
    recommended_action: str
    estimated_cost_impact: Optional[Dict[str, Any]] = None
    estimated_energy_impact: Optional[Dict[str, Any]] = None
    estimated_carbon_impact: Optional[Dict[str, Any]] = None
    implementation_effort: str
    confidence: float
    status: str
    policy_status: str
    policy_notes: Optional[str] = None
    created_at: datetime
    reviewed_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ----------------------------------------------------
# 4. Impact Measurement Schemas
# ----------------------------------------------------
class GreenImpactResponse(BaseModel):
    id: str
    opportunity_id: str
    business_profile_id: str
    metric_name: str
    unit: str
    baseline_value: float
    measured_value: Optional[float] = None
    absolute_change: Optional[float] = None
    percentage_change: Optional[float] = None
    is_demo: bool
    verification_status: str
    formula: str
    assumptions: Optional[str] = None
    verified_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class GreenImpactVerifyRequest(BaseModel):
    measured_value: float
    assumptions: Optional[str] = None
    is_demo: bool = False


# ----------------------------------------------------
# 5. Agent Run & Trace Schemas
# ----------------------------------------------------
class AgentRunTraceStep(BaseModel):
    step: str
    status: str
    duration_ms: int
    source_count: int
    summary: str


class AgentRunResponse(BaseModel):
    id: str
    business_profile_id: str
    agent_type: str
    status: str
    input_sources: List[str]
    output_count: int
    trace_steps: List[Dict[str, Any]]
    error: Optional[str] = None
    model_used: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ----------------------------------------------------
# 6. Green Summary & Score Schemas
# ----------------------------------------------------
class ScoreComponent(BaseModel):
    name: str
    score: float
    weight: float
    contribution: float
    description: str


class GreenScoreDetailResponse(BaseModel):
    score: int
    rating: str  # Excellent, Good, Moderate, Needs Attention
    calculation_method: str
    last_updated: str
    components: List[ScoreComponent]


class GreenSummaryResponse(BaseModel):
    business_profile_id: str
    green_score: int
    score_rating: str
    potential_cost_savings: str
    energy_opportunity: str
    estimated_carbon_reduction: str
    open_opportunities_count: int
    verified_impacts_count: int
    data_quality: str  # HIGH, MEDIUM, LOW, INSUFFICIENT
    data_quality_notes: str
    top_opportunities: List[GreenOpportunityResponse]
