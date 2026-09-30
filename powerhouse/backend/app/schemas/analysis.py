from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class AnalysisSummaryCounts(BaseModel):
    total_approvals: int = 0
    completed_approvals: int = 0
    in_progress_approvals: int = 0
    pending_approvals: int = 0
    high_priority_approvals: int = 0
    total_compliance_tasks: int = 0
    upcoming_tasks: int = 0
    total_required_documents: int = 0
    total_recommended_schemes: int = 0
    compliance_score: int = 78


class BusinessAnalysisResponse(BaseModel):
    id: str
    business_profile_id: str
    analysis_version: str
    risk_level: str
    analysis_status: str
    total_approvals: int
    high_priority_approvals: int
    total_compliance_tasks: int
    total_required_documents: int
    total_recommended_schemes: int
    compliance_score: int
    analysis_result: Dict[str, Any]
    analysis_date: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
