from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class GovernmentSchemeBase(BaseModel):
    name: str
    short_name: Optional[str] = None
    description: Optional[str] = None
    benefit: str
    category: str
    match_score: int = 0
    match_reason: Optional[List[str]] = None
    eligibility_status: str = "Eligible"
    official_source: Optional[str] = None
    deadline: Optional[str] = None


class GovernmentSchemeCreate(GovernmentSchemeBase):
    business_profile_id: str
    analysis_id: Optional[str] = None


class GovernmentSchemeResponse(GovernmentSchemeBase):
    id: str
    business_profile_id: str
    analysis_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
