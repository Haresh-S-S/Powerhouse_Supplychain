import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class GreenOperationalMetric(Base):
    __tablename__ = "green_operational_metrics"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    business_profile_id = Column(String(36), ForeignKey("business_profiles.id", ondelete="CASCADE"), nullable=False, index=True)

    metric_type = Column(String(100), nullable=False, index=True)  # cpu_utilization, memory_utilization, daily_kwh, idle_compute_hours, paper_reams_consumed, redundant_inference_pct
    value = Column(Float, nullable=False)
    unit = Column(String(50), nullable=False)  # %, kWh, hours, reams

    is_demo = Column(Boolean, nullable=False, default=False)
    label = Column(String(255), nullable=True)  # e.g., 'DEMO DATA — Core Cloud Worker Node 1'
    collected_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    business_profile = relationship("BusinessProfile", back_populates="green_operational_metrics")
