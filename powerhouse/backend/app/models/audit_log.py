import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, JSON
from app.core.database import Base


class AuditLog(Base):
    __tablename__ = 'audit_logs'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    business_profile_id = Column(String(36), ForeignKey('business_profiles.id', ondelete='CASCADE'), nullable=False, index=True)

    user_name = Column(String(100), nullable=False, default='Mohith K')
    user_id = Column(String(36), nullable=True)
    action = Column(String(100), nullable=False)
    target_entity_type = Column(String(100), nullable=False)
    target_entity_name = Column(String(255), nullable=False)
    previous_state = Column(String(100), nullable=True)
    new_state = Column(String(100), nullable=True)
    source = Column(String(255), nullable=False)
    proposal_id = Column(String(36), nullable=True)

    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    details = Column(JSON, nullable=True)
