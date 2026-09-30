from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class DocumentBase(BaseModel):
    name: str
    category: str
    file_name: Optional[str] = None
    file_type: str = "PDF"
    file_size: Optional[str] = None
    status: str = "Verified"
    required: bool = True
    upload_date: Optional[str] = None
    expiry_date: Optional[str] = None
    verification_date: Optional[str] = None
    renewal_cycle: Optional[str] = None
    storage_path: Optional[str] = None
    content_hash: Optional[str] = None
    analysis_status: Optional[str] = "Uploaded"
    extracted_data: Optional[str] = None


class DocumentCreate(DocumentBase):
    business_profile_id: str
    approval_id: Optional[str] = None


class DocumentUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    file_name: Optional[str] = None
    file_type: Optional[str] = None
    file_size: Optional[str] = None
    status: Optional[str] = None
    required: Optional[bool] = None
    upload_date: Optional[str] = None
    expiry_date: Optional[str] = None
    verification_date: Optional[str] = None
    renewal_cycle: Optional[str] = None
    storage_path: Optional[str] = None
    content_hash: Optional[str] = None
    analysis_status: Optional[str] = None
    extracted_data: Optional[str] = None


class DocumentResponse(DocumentBase):
    id: str
    business_profile_id: str
    approval_id: Optional[str] = None
    mapped_approval: Optional[str] = None
    evidence_status: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
