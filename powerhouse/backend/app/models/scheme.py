import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base


class GovernmentScheme(Base):
    __tablename__ = "government_schemes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    business_profile_id = Column(String(36), ForeignKey("business_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    analysis_id = Column(String(36), nullable=True)

    name = Column(String(255), nullable=False)
    short_name = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    benefit = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False)
    match_score = Column(Integer, nullable=False, default=0)
    match_reason = Column(JSON, nullable=True)
    eligibility_status = Column(String(50), nullable=False, default="Eligible")
    official_source = Column(String(255), nullable=True)
    deadline = Column(String(100), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    business_profile = relationship("BusinessProfile", back_populates="schemes")
