from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class SupplierDocumentBase(BaseModel):
    document_name: str
    document_type: str
    verification_status: str = "Pending"
    expiry_date: Optional[str] = None
    document_id: Optional[str] = None


class SupplierDocumentResponse(SupplierDocumentBase):
    id: str
    supplier_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SupplierBase(BaseModel):
    name: str
    supplier_type: str = "Raw Material"
    location: str
    country: str = "India"
    products_or_materials: List[str] = Field(default_factory=list)
    dependency_percentage: float = 0.0
    lead_time_days: int = 7
    status: str = "Active"
    contact_information: Optional[Dict[str, Any]] = None
    risk_status: str = "Low"


class SupplierCreate(SupplierBase):
    pass


class SupplierResponse(SupplierBase):
    id: str
    business_id: str
    is_demo: bool
    created_at: datetime
    updated_at: datetime
    documents: List[SupplierDocumentResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True


class SupplyItemBase(BaseModel):
    name: str
    category: str = "Raw Material"
    criticality: str = "High"
    primary_supplier_id: Optional[str] = None
    alternate_supplier_count: int = 0
    dependency_percentage: float = 100.0
    monthly_consumption: Optional[str] = None
    buffer_stock_days: int = 15


class SupplyItemCreate(SupplyItemBase):
    pass


class SupplyItemResponse(SupplyItemBase):
    id: str
    business_id: str
    is_demo: bool
    created_at: datetime
    updated_at: datetime
    primary_supplier_name: Optional[str] = None

    class Config:
        from_attributes = True


class SupplyChainRiskResponse(BaseModel):
    id: str
    business_id: str
    supplier_id: Optional[str] = None
    supply_item_id: Optional[str] = None
    supplier_name: Optional[str] = None
    supply_item_name: Optional[str] = None
    title: str
    category: str
    priority: str
    severity: str
    evidence: Dict[str, Any]
    issue: str
    cause: str
    recommended_action: str
    estimated_cost: float
    estimated_risk_reduction: float
    effort: str
    confidence: float
    status: str
    policy_check_status: str
    is_demo: bool
    detected_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SupplyChainSummaryResponse(BaseModel):
    business_id: str
    total_suppliers: int
    critical_suppliers: int
    total_items: int
    critical_items: int
    single_source_count: int
    missing_docs_count: int
    overall_resilience_score: int  # 0 to 100
    resilience_rating: str  # Excellent, Resilient, Moderate, Vulnerable, High Risk
    active_risks_count: int
    top_risks: List[SupplyChainRiskResponse] = Field(default_factory=list)
    lead_time_average_days: float
