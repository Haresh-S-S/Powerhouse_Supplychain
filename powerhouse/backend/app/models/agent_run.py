import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base


class AgentRun(Base):
    __tablename__ = "agent_runs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    business_profile_id = Column(String(36), ForeignKey("business_profiles.id", ondelete="CASCADE"), nullable=False, index=True)

    agent_type = Column(String(100), nullable=False)  # GreenAgentOrchestrator, EnergyAgent, GreenComputingAgent, etc.
    status = Column(String(50), nullable=False, default="RUNNING")  # RUNNING, COMPLETED, FAILED, INSUFFICIENT_DATA

    input_sources = Column(JSON, nullable=False)  # List of sources consumed (e.g., business_profile, tasks, documents, metrics)
    output_count = Column(Integer, nullable=False, default=0)
    trace_steps = Column(JSON, nullable=False)  # [{step: 'Observe', status: 'COMPLETED', duration_ms: 12, summary: '...'}]

    error = Column(Text, nullable=True)
    model_used = Column(String(100), nullable=True)

    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    business_profile = relationship("BusinessProfile", back_populates="agent_runs")
