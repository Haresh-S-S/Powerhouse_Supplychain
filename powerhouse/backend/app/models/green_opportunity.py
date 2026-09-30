import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base


class GreenOpportunity(Base):
    __tablename__ = "green_opportunities"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    business_profile_id = Column(String(36), ForeignKey("business_profiles.id", ondelete="CASCADE"), nullable=False, index=True)

    agent_type = Column(String(100), nullable=False)
    title = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False)  # Compute Efficiency, Energy Optimization, Workflow Digitization, Resource & Waste
    priority = Column(String(50), nullable=False, default="Medium")  # High, Medium, Low
    severity = Column(String(50), nullable=False, default="Warning")  # Critical, Warning, Info

    detected_issue = Column(Text, nullable=False)
    evidence = Column(JSON, nullable=False)  # List of structured observation dicts
    cause = Column(Text, nullable=False)
    recommended_action = Column(Text, nullable=False)

    estimated_cost_impact = Column(JSON, nullable=True)   # {value, unit, currency, tariff, assumptions}
    estimated_energy_impact = Column(JSON, nullable=True) # {value, unit, formula, assumptions}
    estimated_carbon_impact = Column(JSON, nullable=True) # {value, unit, factor_id, factor_source, assumptions}

    implementation_effort = Column(String(50), nullable=False, default="Medium")  # Low, Medium, High
    confidence = Column(Float, nullable=False, default=0.85)

    # Lifecycle statuses: DETECTED, UNDER_REVIEW, APPROVED, REJECTED, TASK_CREATED, IN_PROGRESS, COMPLETED, VERIFIED, INSUFFICIENT_DATA
    status = Column(String(50), nullable=False, default="DETECTED", index=True)

    # Policy validation status: PASS, BLOCK, REVIEW_REQUIRED
    policy_status = Column(String(50), nullable=False, default="PASS")
    policy_notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    reviewed_at = Column(DateTime, nullable=True)
    approved_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    business_profile = relationship("BusinessProfile", back_populates="green_opportunities")
    impact_measurements = relationship("GreenImpactMeasurement", back_populates="opportunity", cascade="all, delete-orphan")
