from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class BusinessProfileBase(BaseModel):
    business_name: str
    business_type: str
    industry: str
    sector: Optional[str] = None
    established_date: Optional[str] = None
    company_size: str
    employee_count: int = 1
    annual_turnover: Optional[str] = None

    registered_address: Optional[str] = None
    city: str
    state: str
    country: str = "India"
    postal_code: Optional[str] = None

    primary_activity: Optional[str] = None
    secondary_activities: Optional[str] = None
    manufacturing_activity: bool = True
    import_activities: bool = False
    export_activities: bool = False
    environmental_impact: str = "Moderate"
    operating_status: str = "Active"

    has_gst: bool = True
    has_msme_registration: bool = True
    has_udyam_registration: bool = True

    cin: Optional[str] = None
    pan: Optional[str] = None
    gstin: Optional[str] = None
    udyam_number: Optional[str] = None

    user_id: Optional[str] = None
    onboarding_completed: bool = False
    business_category: Optional[str] = None
    image_category: Optional[str] = None


class BusinessProfileCreate(BusinessProfileBase):
    pass


class BusinessProfileUpdate(BaseModel):
    business_name: Optional[str] = None
    business_type: Optional[str] = None
    industry: Optional[str] = None
    sector: Optional[str] = None
    established_date: Optional[str] = None
    company_size: Optional[str] = None
    employee_count: Optional[int] = None
    annual_turnover: Optional[str] = None

    registered_address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None

    primary_activity: Optional[str] = None
    secondary_activities: Optional[str] = None
    manufacturing_activity: Optional[bool] = None
    import_activities: Optional[bool] = None
    export_activities: Optional[bool] = None
    environmental_impact: Optional[str] = None
    operating_status: Optional[str] = None

    has_gst: Optional[bool] = None
    has_msme_registration: Optional[bool] = None
    has_udyam_registration: Optional[bool] = None

    cin: Optional[str] = None
    pan: Optional[str] = None
    gstin: Optional[str] = None
    udyam_number: Optional[str] = None

    user_id: Optional[str] = None
    onboarding_completed: Optional[bool] = None
    business_category: Optional[str] = None
    image_category: Optional[str] = None


class BusinessProfileResponse(BusinessProfileBase):
    id: str
    user_id: Optional[str] = None
    onboarding_completed: bool = False
    business_category: Optional[str] = None
    image_category: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
