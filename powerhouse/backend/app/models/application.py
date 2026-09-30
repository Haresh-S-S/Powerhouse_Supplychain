import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base


class Application(Base):
    __tablename__ = "applications"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    business_profile_id = Column(String(36), ForeignKey("business_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    approval_id = Column(String(36), nullable=True)

    application_number = Column(String(100), nullable=False, index=True)
    department = Column(String(255), nullable=False)
    application_name = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False, default="Submitted")

    submission_date = Column(String(50), nullable=True)
    last_updated = Column(String(50), nullable=True)
    current_stage = Column(String(100), nullable=True)
    timeline = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    business_profile = relationship("BusinessProfile", back_populates="applications")
