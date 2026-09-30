import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, JSON
from app.core.database import Base


class ActionProposal(Base):
    __tablename__ = 'action_proposals'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    business_profile_id = Column(String(36), ForeignKey('business_profiles.id', ondelete='CASCADE'), nullable=False, index=True)

    action_type = Column(String(100), nullable=False)
    title = Column(String(255), nullable=False)
    reason = Column(Text, nullable=False)
    affected_entity_type = Column(String(100), nullable=False)
    affected_entity_id = Column(String(255), nullable=True)
    changes = Column(JSON, nullable=False)
    risk_level = Column(String(50), nullable=False, default='Low')
    status = Column(String(50), nullable=False, default='Pending Review')

    created_by = Column(String(100), nullable=False, default='AI Compliance Advisor')
    confirmed_by = Column(String(100), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
