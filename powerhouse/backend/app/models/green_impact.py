import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class GreenImpactMeasurement(Base):
    __tablename__ = "green_impact_measurements"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    opportunity_id = Column(String(36), ForeignKey("green_opportunities.id", ondelete="CASCADE"), nullable=False, index=True)
    business_profile_id = Column(String(36), ForeignKey("business_profiles.id", ondelete="CASCADE"), nullable=False, index=True)

    metric_name = Column(String(100), nullable=False)  # e.g., CPU Utilization, Daily Energy Consumption, Paper Reams
    unit = Column(String(50), nullable=False)          # %, kWh, reams
    baseline_value = Column(Float, nullable=False)     # Pre-action baseline measurement
    measured_value = Column(Float, nullable=True)      # Post-action measurement (None if pending)
    absolute_change = Column(Float, nullable=True)     # baseline - measured or vice versa
    percentage_change = Column(Float, nullable=True)   # ((baseline - measured) / baseline) * 100

    is_demo = Column(Boolean, nullable=False, default=False)
    verification_status = Column(String(50), nullable=False, default="PENDING")  # VERIFIED, PENDING, INSUFFICIENT_DATA
    formula = Column(String(255), nullable=False)
    assumptions = Column(Text, nullable=True)

    verified_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    opportunity = relationship("GreenOpportunity", back_populates="impact_measurements")
    business_profile = relationship("BusinessProfile", back_populates="green_impact_measurements")
