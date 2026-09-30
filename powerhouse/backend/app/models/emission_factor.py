import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime
from app.core.database import Base


class EmissionFactor(Base):
    __tablename__ = "emission_factors"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    name = Column(String(255), nullable=False, unique=True)
    value = Column(Float, nullable=False)  # Numeric factor, e.g., 0.716
    unit = Column(String(50), nullable=False)  # e.g., kgCO2e/kWh, kgCO2e/ream
    source = Column(String(255), nullable=False)  # e.g., CEA CO2 Baseline Database v19
    source_version = Column(String(50), nullable=True)
    geography = Column(String(100), nullable=False, default="India - National Grid")
    scope = Column(String(50), nullable=False, default="Scope 2")  # Scope 1, Scope 2, Scope 3
    effective_date = Column(String(50), nullable=True)
    review_date = Column(String(50), nullable=True)
    status = Column(String(50), nullable=False, default="VERIFIED")  # VERIFIED, REVIEW_REQUIRED, RETIRED

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
