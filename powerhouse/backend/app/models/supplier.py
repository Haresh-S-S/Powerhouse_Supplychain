import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base


class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    business_id = Column(String(36), ForeignKey("business_profiles.id", ondelete="CASCADE"), nullable=False, index=True)

    name = Column(String(255), nullable=False, index=True)
    supplier_type = Column(String(100), nullable=False, default="Raw Material")  # Raw Material, Component, Packaging, Logistics, Service
    location = Column(String(100), nullable=False)
    country = Column(String(100), nullable=False, default="India")
    products_or_materials = Column(JSON, nullable=False, default=list)  # list of strings or item descriptions
    dependency_percentage = Column(Float, nullable=False, default=0.0)
    lead_time_days = Column(Integer, nullable=False, default=7)
    status = Column(String(50), nullable=False, default="Active")  # Active, Under Review, Inactive
    contact_information = Column(JSON, nullable=True)  # {"contact_person": "...", "phone": "...", "email": "..."}
    risk_status = Column(String(50), nullable=False, default="Low")  # Low, Medium, High, Critical
    is_demo = Column(Boolean, nullable=False, default=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    business_profile = relationship("BusinessProfile", back_populates="suppliers")
    documents = relationship("SupplierDocument", back_populates="supplier", cascade="all, delete-orphan")
    supply_items = relationship("SupplyItem", back_populates="primary_supplier")
    risks = relationship("SupplyChainRisk", back_populates="supplier")


class SupplierDocument(Base):
    __tablename__ = "supplier_documents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    supplier_id = Column(String(36), ForeignKey("suppliers.id", ondelete="CASCADE"), nullable=False, index=True)
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="SET NULL"), nullable=True, index=True)

    document_name = Column(String(255), nullable=False)
    document_type = Column(String(100), nullable=False)  # Quality Certificate, GST Clearance, ISO 9001, Vendor Contract, Safety Audit
    verification_status = Column(String(50), nullable=False, default="Pending")  # Verified, Pending, Expired, Missing
    expiry_date = Column(String(50), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    supplier = relationship("Supplier", back_populates="documents")
    vault_document = relationship("Document")


class SupplyItem(Base):
    __tablename__ = "supply_items"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    business_id = Column(String(36), ForeignKey("business_profiles.id", ondelete="CASCADE"), nullable=False, index=True)

    name = Column(String(255), nullable=False, index=True)
    category = Column(String(100), nullable=False, default="Raw Material")  # Raw Material, Packaging, Component, Consumable
    criticality = Column(String(50), nullable=False, default="High")  # Critical, High, Medium, Low
    primary_supplier_id = Column(String(36), ForeignKey("suppliers.id", ondelete="SET NULL"), nullable=True, index=True)
    alternate_supplier_count = Column(Integer, nullable=False, default=0)
    dependency_percentage = Column(Float, nullable=False, default=100.0)
    monthly_consumption = Column(String(100), nullable=True)
    buffer_stock_days = Column(Integer, nullable=False, default=15)
    is_demo = Column(Boolean, nullable=False, default=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    business_profile = relationship("BusinessProfile", back_populates="supply_items")
    primary_supplier = relationship("Supplier", back_populates="supply_items")
    risks = relationship("SupplyChainRisk", back_populates="supply_item")


class SupplyChainRisk(Base):
    __tablename__ = "supply_chain_risks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    business_id = Column(String(36), ForeignKey("business_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    supplier_id = Column(String(36), ForeignKey("suppliers.id", ondelete="SET NULL"), nullable=True, index=True)
    supply_item_id = Column(String(36), ForeignKey("supply_items.id", ondelete="SET NULL"), nullable=True, index=True)

    title = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False)  # Single Supplier Dependency, Missing Documentation, Extended Lead Time, Geographic Concentration, Critical Buffer Depletion
    priority = Column(String(50), nullable=False, default="High")  # Critical, High, Medium, Low
    severity = Column(String(50), nullable=False, default="Warning")  # Critical, Warning, Info
    evidence = Column(JSON, nullable=False, default=dict)
    issue = Column(Text, nullable=False)
    cause = Column(Text, nullable=False)
    recommended_action = Column(Text, nullable=False)
    estimated_cost = Column(Float, nullable=False, default=0.0)
    estimated_risk_reduction = Column(Float, nullable=False, default=0.0)
    effort = Column(String(50), nullable=False, default="Medium")  # Low, Medium, High
    confidence = Column(Float, nullable=False, default=0.85)
    status = Column(String(50), nullable=False, default="DETECTED")  # DETECTED, ANALYZING, RECOMMENDED, VALIDATED, AWAITING_APPROVAL, APPROVED, ACTION_CREATED, MONITORING, RESOLVED, DISMISSED
    policy_check_status = Column(String(50), nullable=False, default="PASS")  # PASS, REVIEW_REQUIRED, BLOCK
    is_demo = Column(Boolean, nullable=False, default=False)

    detected_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    business_profile = relationship("BusinessProfile", back_populates="supply_chain_risks")
    supplier = relationship("Supplier", back_populates="risks")
    supply_item = relationship("SupplyItem", back_populates="risks")
