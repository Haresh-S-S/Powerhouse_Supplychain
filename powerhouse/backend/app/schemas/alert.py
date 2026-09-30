from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class AlertBase(BaseModel):
    title: str
    description: Optional[str] = None
    severity: str = "information"
    category: str
    is_read: bool = False
    action_url: Optional[str] = None
    related_entity_type: Optional[str] = None
    related_entity_id: Optional[str] = None
    due_date: Optional[str] = None


class AlertCreate(AlertBase):
    business_profile_id: str


class AlertUpdate(BaseModel):
    is_read: Optional[bool] = None
    title: Optional[str] = None
    description: Optional[str] = None


class AlertResponse(AlertBase):
    id: str
    business_profile_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
