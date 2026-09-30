from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from app.services.green.emission_factors import EmissionFactorService


class ImpactCalculationService:
    # Default industrial / commercial HT energy tariff for calculations (INR per kWh)
    DEFAULT_COMMERCIAL_TARIFF_INR = 7.50

    @staticmethod
    def calculate_energy_savings(
        baseline_kwh: float,
        projected_kwh: float,
        assumptions: str = "Estimated from operational telemetry and idle load reduction."
    ) -> Dict[str, Any]:
        """
        Deterministic energy reduction calculation:
        difference_kwh = baseline_kwh - projected_kwh
        """
        if baseline_kwh is None or projected_kwh is None or baseline_kwh <= 0:
            return {
                "value": None,
                "unit": "kWh",
                "formula": "baseline_kwh - projected_kwh",
                "status": "DATA_REQUIRED",
                "message": "Insufficient energy data to calculate reduction."
            }

        diff_kwh = round(baseline_kwh - projected_kwh, 2)
        pct = round((diff_kwh / baseline_kwh) * 100, 1)

        return {
            "value": diff_kwh,
            "unit": "kWh/month",
            "percentage": pct,
            "baseline_kwh": baseline_kwh,
            "projected_kwh": projected_kwh,
            "formula": "baseline_kwh - projected_kwh",
            "assumptions": assumptions,
            "timestamp": datetime.utcnow().isoformat()
        }

    @staticmethod
    def calculate_cost_savings(
        energy_reduction_kwh: Optional[float],
        tariff_per_kwh: float = DEFAULT_COMMERCIAL_TARIFF_INR,
        currency: str = "INR",
        assumptions: str = "Calculated at Tamil Nadu / Indian commercial HT electricity tariff rate of ₹7.50/kWh."
    ) -> Dict[str, Any]:
        """
        Deterministic financial impact calculation:
        cost_savings = energy_reduction_kwh * tariff_per_kwh
        """
        if energy_reduction_kwh is None or energy_reduction_kwh <= 0 or tariff_per_kwh is None or tariff_per_kwh <= 0:
            return {
                "value": None,
                "currency": currency,
                "status": "UNAVAILABLE",
                "message": "Financial impact cannot be estimated with current data."
            }

        savings = round(energy_reduction_kwh * tariff_per_kwh, 2)

        return {
            "value": savings,
            "currency": currency,
            "tariff_per_kwh": tariff_per_kwh,
            "formula": "energy_reduction_kwh * tariff_per_kwh",
            "assumptions": assumptions,
            "timestamp": datetime.utcnow().isoformat()
        }

    @staticmethod
    def calculate_carbon_savings(
        db: Session,
        energy_reduction_kwh: Optional[float] = None,
        paper_reams_saved: Optional[float] = None,
        geography: str = "India - National Grid"
    ) -> Dict[str, Any]:
        """
        Deterministic carbon reduction calculation using verified emission factors.
        carbon_kg = energy_reduction_kwh * verified_emission_factor
        """
        if energy_reduction_kwh is not None and energy_reduction_kwh > 0:
            factor = EmissionFactorService.get_verified_factor_by_name(db, "National Grid Baseline")
            if not factor or factor.status != "VERIFIED":
                return {
                    "value": None,
                    "unit": "kgCO2e",
                    "status": "UNCONFIGURED",
                    "message": "Carbon impact unavailable — emission factor not configured."
                }

            carbon_kg = round(energy_reduction_kwh * factor.value, 2)
            return {
                "value": carbon_kg,
                "unit": "kgCO2e/month",
                "formula": "energy_reduction_kwh * emission_factor",
                "factor_id": factor.id,
                "factor_name": factor.name,
                "factor_value": factor.value,
                "factor_unit": factor.unit,
                "factor_source": factor.source,
                "scope": factor.scope,
                "assumptions": f"Applied verified CEA National Grid Baseline v19 ({factor.value} {factor.unit}).",
                "timestamp": datetime.utcnow().isoformat()
            }

        elif paper_reams_saved is not None and paper_reams_saved > 0:
            factor = EmissionFactorService.get_verified_factor_by_name(db, "Office Paper")
            if not factor or factor.status != "VERIFIED":
                return {
                    "value": None,
                    "unit": "kgCO2e",
                    "status": "UNCONFIGURED",
                    "message": "Carbon impact unavailable — emission factor not configured."
                }

            carbon_kg = round(paper_reams_saved * factor.value, 2)
            return {
                "value": carbon_kg,
                "unit": "kgCO2e/year",
                "formula": "paper_reams_saved * emission_factor",
                "factor_id": factor.id,
                "factor_name": factor.name,
                "factor_value": factor.value,
                "factor_unit": factor.unit,
                "factor_source": factor.source,
                "scope": factor.scope,
                "assumptions": f"Applied verified EPA WARM paper factor ({factor.value} {factor.unit}) for digitized statutory filings.",
                "timestamp": datetime.utcnow().isoformat()
            }

        return {
            "value": None,
            "unit": "kgCO2e",
            "status": "DATA_REQUIRED",
            "message": "Carbon impact unavailable — operational reduction metrics required."
        }
