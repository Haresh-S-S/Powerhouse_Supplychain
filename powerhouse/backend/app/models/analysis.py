import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base


class BusinessAnalysis(Base):
    __tablename__ = "business_analyses"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    business_profile_id = Column(String(36), ForeignKey("business_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    analysis_version = Column(String(20), nullable=False, default="1.0")
    risk_level = Column(String(50), nullable=False, default="Medium")
    analysis_status = Column(String(50), nullable=False, default="Completed")

    total_approvals = Column(Integer, nullable=False, default=0)
    high_priority_approvals = Column(Integer, nullable=False, default=0)
    total_compliance_tasks = Column(Integer, nullable=False, default=0)
    total_required_documents = Column(Integer, nullable=False, default=0)
    total_recommended_schemes = Column(Integer, nullable=False, default=0)
    compliance_score = Column(Integer, nullable=False, default=78)

    # Full structured analysis result JSON (includes approvals, tasks, docs, schemes, insights)
    analysis_result = Column(JSON, nullable=False)
    analysis_date = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    business_profile = relationship("BusinessProfile", back_populates="analyses")
