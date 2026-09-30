import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    business_profile_id = Column(String(36), ForeignKey("business_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    approval_id = Column(String(36), nullable=True)

    name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False)
    file_name = Column(String(255), nullable=True)
    file_type = Column(String(50), nullable=False, default="PDF")
    file_size = Column(String(50), nullable=True)
    status = Column(String(50), nullable=False, default="Verified")
    required = Column(Boolean, nullable=False, default=True)

    upload_date = Column(String(50), nullable=True)
    expiry_date = Column(String(50), nullable=True)
    verification_date = Column(String(50), nullable=True)
    renewal_cycle = Column(String(50), nullable=True)
    storage_path = Column(String(500), nullable=True)
    content_hash = Column(String(64), nullable=True, index=True)
    analysis_status = Column(String(50), nullable=False, default="Uploaded")
    extracted_data = Column(String(4000), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    business_profile = relationship("BusinessProfile", back_populates="documents")
