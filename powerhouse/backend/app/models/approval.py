import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base


class Approval(Base):
    __tablename__ = "approvals"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    business_profile_id = Column(String(36), ForeignKey("business_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    analysis_id = Column(String(36), nullable=True)

    name = Column(String(255), nullable=False)
    authority = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    priority = Column(String(50), nullable=False, default="High")
    status = Column(String(50), nullable=False, default="Pending")
    trigger_reason = Column(Text, nullable=True)

    required_documents_count = Column(Integer, nullable=False, default=0)
    progress_percentage = Column(Integer, nullable=False, default=0)
    due_date = Column(String(100), nullable=True)
    steps = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    business_profile = relationship("BusinessProfile", back_populates="approvals")
