from typing import Optional, List, Any, Dict
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ApprovalBase(BaseModel):
    name: str
    authority: str
    category: str
    description: Optional[str] = None
    priority: str = "High"
    status: str = "Pending"
    trigger_reason: Optional[str] = None
    required_documents_count: int = 0
    progress_percentage: int = 0
    due_date: Optional[str] = None
    steps: Optional[List[Dict[str, Any]]] = None


class ApprovalCreate(ApprovalBase):
    business_profile_id: str
    analysis_id: Optional[str] = None


class ApprovalUpdate(BaseModel):
    name: Optional[str] = None
    authority: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    trigger_reason: Optional[str] = None
    required_documents_count: Optional[int] = None
    progress_percentage: Optional[int] = None
    due_date: Optional[str] = None
    steps: Optional[List[Dict[str, Any]]] = None


class ApprovalResponse(ApprovalBase):
    id: str
    business_profile_id: str
    analysis_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
