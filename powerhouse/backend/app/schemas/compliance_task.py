from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ComplianceTaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    category: str = "Statutory Filing"
    priority: str = "High"
    status: str = "Upcoming"
    due_date: str
    estimated_days: int = 0
    assignee: Optional[str] = None


class ComplianceTaskCreate(ComplianceTaskBase):
    business_profile_id: str
    approval_id: Optional[str] = None


class ComplianceTaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    due_date: Optional[str] = None
    estimated_days: Optional[int] = None
    assignee: Optional[str] = None
    completed_at: Optional[datetime] = None


class ComplianceTaskResponse(ComplianceTaskBase):
    id: str
    business_profile_id: str
    approval_id: Optional[str] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
