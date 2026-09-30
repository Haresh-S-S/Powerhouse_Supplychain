from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ApplicationBase(BaseModel):
    application_number: str
    department: str
    application_name: str
    status: str = "Submitted"
    submission_date: Optional[str] = None
    last_updated: Optional[str] = None
    current_stage: Optional[str] = None
    timeline: Optional[List[Dict[str, Any]]] = None


class ApplicationCreate(ApplicationBase):
    business_profile_id: str
    approval_id: Optional[str] = None


class ApplicationUpdate(BaseModel):
    application_number: Optional[str] = None
    department: Optional[str] = None
    application_name: Optional[str] = None
    status: Optional[str] = None
    submission_date: Optional[str] = None
    last_updated: Optional[str] = None
    current_stage: Optional[str] = None
    timeline: Optional[List[Dict[str, Any]]] = None


class ApplicationResponse(ApplicationBase):
    id: str
    business_profile_id: str
    approval_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
