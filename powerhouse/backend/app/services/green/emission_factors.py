import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.emission_factor import EmissionFactor

DEFAULT_FACTORS = [
    {
        "name": "Central Electricity Authority (CEA) India National Grid Baseline",
        "value": 0.716,
        "unit": "kgCO2e/kWh",
        "source": "CEA CO2 Baseline Database for the Indian Power Sector, Version 19.0 (User Guide Table 1)",
        "source_version": "v19.0",
        "geography": "India - National Grid",
        "scope": "Scope 2 (Indirect - Purchased Electricity)",
        "effective_date": "2024-01-01",
        "review_date": "2025-12-31",
        "status": "VERIFIED",
    },
    {
        "name": "CEA Southern Regional Grid Specific Operating Margin",
        "value": 0.732,
        "unit": "kgCO2e/kWh",
        "source": "CEA India Regional Electricity Database, Southern Grid Baseline",
        "source_version": "v18.2",
        "geography": "India - Southern Region (TN/KA/AP/KL/TS)",
        "scope": "Scope 2 (Purchased Electricity)",
        "effective_date": "2023-06-01",
        "review_date": "2025-06-01",
        "status": "VERIFIED",
    },
    {
        "name": "EPA WARM Virgin Pulp Office Paper Lifecycle Emissions",
        "value": 4.60,
        "unit": "kgCO2e/ream",
        "source": "US EPA Waste Reduction Model (WARM) - Office Paper Lifecycle & Transport Factors",
        "source_version": "WARM v15",
        "geography": "Global Standard Reference",
        "scope": "Scope 3 (Purchased Goods & Services / Paper Waste)",
        "effective_date": "2023-01-01",
        "review_date": "2026-01-01",
        "status": "VERIFIED",
    },
]


class EmissionFactorService:
    @staticmethod
    def ensure_default_factors(db: Session) -> None:
        """Seed default verified Indian statutory & standard emission factors if not present."""
        for item in DEFAULT_FACTORS:
            existing = db.query(EmissionFactor).filter(EmissionFactor.name == item["name"]).first()
            if not existing:
                factor = EmissionFactor(
                    id=str(uuid.uuid4()),
                    name=item["name"],
                    value=item["value"],
                    unit=item["unit"],
                    source=item["source"],
                    source_version=item.get("source_version"),
                    geography=item["geography"],
                    scope=item["scope"],
                    effective_date=item.get("effective_date"),
                    review_date=item.get("review_date"),
                    status=item["status"],
                )
                db.add(factor)
        db.commit()

    @staticmethod
    def get_all_factors(db: Session) -> List[EmissionFactor]:
        EmissionFactorService.ensure_default_factors(db)
        return db.query(EmissionFactor).order_by(EmissionFactor.status.desc(), EmissionFactor.name).all()

    @staticmethod
    def get_verified_factor_by_name(db: Session, name_substring: str) -> Optional[EmissionFactor]:
        EmissionFactorService.ensure_default_factors(db)
        return (
            db.query(EmissionFactor)
            .filter(
                EmissionFactor.name.ilike(f"%{name_substring}%"),
                EmissionFactor.status == "VERIFIED",
            )
            .first()
        )
