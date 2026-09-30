import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class BusinessProfile(Base):
    __tablename__ = "business_profiles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    onboarding_completed = Column(Boolean, nullable=False, default=False)
    business_category = Column(String(100), nullable=True, index=True)
    image_category = Column(String(100), nullable=True)

    business_name = Column(String(255), nullable=False, index=True)
    business_type = Column(String(100), nullable=False)
    industry = Column(String(100), nullable=False)
    sector = Column(String(100), nullable=True)
    established_date = Column(String(50), nullable=True)
    company_size = Column(String(100), nullable=False)
    employee_count = Column(Integer, nullable=False, default=1)
    annual_turnover = Column(String(100), nullable=True)

    registered_address = Column(Text, nullable=True)
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    country = Column(String(100), nullable=False, default="India")
    postal_code = Column(String(20), nullable=True)

    primary_activity = Column(Text, nullable=True)
    secondary_activities = Column(Text, nullable=True)
    manufacturing_activity = Column(Boolean, nullable=False, default=True)
    import_activities = Column(Boolean, nullable=False, default=False)
    export_activities = Column(Boolean, nullable=False, default=False)
    environmental_impact = Column(String(50), nullable=False, default="Moderate")
    operating_status = Column(String(50), nullable=False, default="Active")

    has_gst = Column(Boolean, nullable=False, default=True)
    has_msme_registration = Column(Boolean, nullable=False, default=True)
    has_udyam_registration = Column(Boolean, nullable=False, default=True)

    cin = Column(String(50), nullable=True)
    pan = Column(String(50), nullable=True)
    gstin = Column(String(50), nullable=True)
    udyam_number = Column(String(50), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="business_profiles")
    analyses = relationship("BusinessAnalysis", back_populates="business_profile", cascade="all, delete-orphan")
    approvals = relationship("Approval", back_populates="business_profile", cascade="all, delete-orphan")
    compliance_tasks = relationship("ComplianceTask", back_populates="business_profile", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="business_profile", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="business_profile", cascade="all, delete-orphan")
    schemes = relationship("GovernmentScheme", back_populates="business_profile", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="business_profile", cascade="all, delete-orphan")
    green_opportunities = relationship("GreenOpportunity", back_populates="business_profile", cascade="all, delete-orphan")
    green_impact_measurements = relationship("GreenImpactMeasurement", back_populates="business_profile", cascade="all, delete-orphan")
    agent_runs = relationship("AgentRun", back_populates="business_profile", cascade="all, delete-orphan")
    green_operational_metrics = relationship("GreenOperationalMetric", back_populates="business_profile", cascade="all, delete-orphan")
    suppliers = relationship("Supplier", back_populates="business_profile", cascade="all, delete-orphan")
    supply_items = relationship("SupplyItem", back_populates="business_profile", cascade="all, delete-orphan")
    supply_chain_risks = relationship("SupplyChainRisk", back_populates="business_profile", cascade="all, delete-orphan")
    employee_profiles = relationship("EmployeeProfile", back_populates="business_profile", cascade="all, delete-orphan")
    role_profiles = relationship("RoleProfile", back_populates="business_profile", cascade="all, delete-orphan")
    skill_gaps = relationship("SkillGap", back_populates="business_profile", cascade="all, delete-orphan")
    learning_paths = relationship("LearningPath", back_populates="business_profile", cascade="all, delete-orphan")
