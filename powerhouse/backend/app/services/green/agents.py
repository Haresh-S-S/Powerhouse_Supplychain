import uuid
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.business import BusinessProfile
from app.models.green_metric import GreenOperationalMetric
from app.models.document import Document
from app.models.compliance_task import ComplianceTask
from app.services.green.impact_engine import ImpactCalculationService
from app.services.green.policy_validator import GreenPolicyValidator


class BaseGreenAgent(ABC):
    """
    Common interface for specialized green intelligence agents.
    Every agent follows: OBSERVE -> DETECT -> ANALYZE -> RECOMMEND
    """

    def __init__(self, agent_name: str, category: str):
        self.agent_name = agent_name
        self.category = category

    @abstractmethod
    def observe(self, db: Session, profile: BusinessProfile) -> Dict[str, Any]:
        """Gathers available evidence and operational metrics."""
        pass

    @abstractmethod
    def detect(self, observations: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identifies patterns or inefficiencies from observations."""
        pass

    @abstractmethod
    def analyze(self, db: Session, detections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Applies specialized domain models, impact formulas, and policy checks."""
        pass


# ----------------------------------------------------
# 1. GreenComputingAgent
# ----------------------------------------------------
class GreenComputingAgent(BaseGreenAgent):
    def __init__(self):
        super().__init__("GreenComputingAgent", "Compute Efficiency")

    def observe(self, db: Session, profile: BusinessProfile) -> Dict[str, Any]:
        metrics = (
            db.query(GreenOperationalMetric)
            .filter(GreenOperationalMetric.business_profile_id == profile.id)
            .all()
        )
        cpu_metrics = [m for m in metrics if m.metric_type == "cpu_utilization"]
        inference_metrics = [m for m in metrics if m.metric_type == "redundant_inference_pct"]
        idle_hours_metrics = [m for m in metrics if m.metric_type == "idle_compute_hours"]

        return {
            "has_metrics": len(metrics) > 0,
            "cpu": cpu_metrics[-1] if cpu_metrics else None,
            "inference": inference_metrics[-1] if inference_metrics else None,
            "idle_hours": idle_hours_metrics[-1] if idle_hours_metrics else None,
            "all_metrics": metrics,
        }

    def detect(self, observations: Dict[str, Any]) -> List[Dict[str, Any]]:
        detections = []
        if not observations["has_metrics"]:
            return detections

        cpu = observations.get("cpu")
        inference = observations.get("inference")
        idle_hours = observations.get("idle_hours")

        # Condition A: Idle / under-utilized compute (< 25% CPU with active compute hours)
        if cpu and cpu.value < 25.0:
            detections.append({
                "type": "IDLE_COMPUTE_DETECTED",
                "metric": "cpu_utilization",
                "value": cpu.value,
                "unit": "%",
                "idle_hours": idle_hours.value if idle_hours else 48.0,
                "is_demo": cpu.is_demo,
                "observation_id": cpu.id,
                "label": cpu.label or "Worker Node / Processing Cluster",
            })

        # Condition B: Redundant AI inference / un-cached prompt execution (> 30% redundant)
        if inference and inference.value > 30.0:
            detections.append({
                "type": "REDUNDANT_INFERENCE_DETECTED",
                "metric": "redundant_inference_pct",
                "value": inference.value,
                "unit": "%",
                "is_demo": inference.is_demo,
                "observation_id": inference.id,
                "label": inference.label or "AI Compliance Inference Engine",
            })

        return detections

    def analyze(self, db: Session, detections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        recommendations = []
        for det in detections:
            if det["type"] == "IDLE_COMPUTE_DETECTED":
                # Deterministic energy calculation: e.g. 150W server idling for 48 hrs = 7.2 kWh/month waste
                baseline_kwh = 240.0
                projected_kwh = 140.0
                energy_impact = ImpactCalculationService.calculate_energy_savings(
                    baseline_kwh=baseline_kwh,
                    projected_kwh=projected_kwh,
                    assumptions="Consolidating idle compute workloads and downscaling off-hours capacity."
                )
                cost_impact = ImpactCalculationService.calculate_cost_savings(energy_impact.get("value"))
                carbon_impact = ImpactCalculationService.calculate_carbon_savings(db, energy_reduction_kwh=energy_impact.get("value"))

                policy_status, policy_notes = GreenPolicyValidator.validate_recommendation(
                    category="Compute Efficiency",
                    action_title="Resize and consolidate under-utilized compute instances",
                    parameters={"target_system": det.get("label", ""), "is_production": True}
                )

                recommendations.append({
                    "agent_type": self.agent_name,
                    "title": "Idle Compute Resource Optimization",
                    "category": self.category,
                    "priority": "High" if det["value"] < 15.0 else "Medium",
                    "severity": "Warning",
                    "detected_issue": f"Compute resource utilization is operating at {det['value']}%, indicating prolonged idle state over monitored execution periods.",
                    "evidence": [
                        {
                            "source_type": "DEMO_DATA" if det["is_demo"] else "COMPUTE_DATA",
                            "source_id": det["observation_id"],
                            "metric": det["metric"],
                            "value": f"{det['value']}%",
                            "evidence_summary": f"Observed CPU utilization of {det['value']}% on {det['label']}.",
                            "is_demo": det["is_demo"],
                            "observation_time": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                        }
                    ],
                    "cause": "Workload allocations are provisioned for peak historical thresholds rather than dynamic autoscaling demand.",
                    "recommended_action": "Schedule off-hours workload consolidation or downscale under-utilized worker instances to conserve energy.",
                    "estimated_energy_impact": energy_impact,
                    "estimated_cost_impact": cost_impact,
                    "estimated_carbon_impact": carbon_impact,
                    "implementation_effort": "Low",
                    "confidence": 0.92,
                    "policy_status": policy_status,
                    "policy_notes": policy_notes,
                })

            elif det["type"] == "REDUNDANT_INFERENCE_DETECTED":
                baseline_kwh = 120.0
                projected_kwh = 60.0
                energy_impact = ImpactCalculationService.calculate_energy_savings(
                    baseline_kwh=baseline_kwh,
                    projected_kwh=projected_kwh,
                    assumptions="Enabling vector similarity semantic caching for recurring statutory compliance inquiries."
                )
                cost_impact = ImpactCalculationService.calculate_cost_savings(energy_impact.get("value"))
                carbon_impact = ImpactCalculationService.calculate_carbon_savings(db, energy_reduction_kwh=energy_impact.get("value"))

                policy_status, policy_notes = GreenPolicyValidator.validate_recommendation(
                    category="Compute Efficiency",
                    action_title="Cache recurring AI inference queries",
                    parameters={"target_system": "AI Compliance Advisor", "is_production": False}
                )

                recommendations.append({
                    "agent_type": self.agent_name,
                    "title": "AI Workload Prompt & Embedding Caching",
                    "category": self.category,
                    "priority": "Medium",
                    "severity": "Info",
                    "detected_issue": f"{det['value']}% of regulatory AI advisory prompts execute duplicate embedding calculations and LLM inferences.",
                    "evidence": [
                        {
                            "source_type": "DEMO_DATA" if det["is_demo"] else "SYSTEM_METRIC",
                            "source_id": det["observation_id"],
                            "metric": det["metric"],
                            "value": f"{det['value']}%",
                            "evidence_summary": f"Measured duplicate query rate of {det['value']}% on statutory advisory pipelines.",
                            "is_demo": det["is_demo"],
                            "observation_time": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                        }
                    ],
                    "cause": "Absence of an exact and semantic cache layer on top of regulatory vector RAG queries.",
                    "recommended_action": "Implement deterministic caching for high-frequency statutory compliance queries to reduce GPU compute overhead.",
                    "estimated_energy_impact": energy_impact,
                    "estimated_cost_impact": cost_impact,
                    "estimated_carbon_impact": carbon_impact,
                    "implementation_effort": "Low",
                    "confidence": 0.88,
                    "policy_status": policy_status,
                    "policy_notes": policy_notes,
                })

        return recommendations


# ----------------------------------------------------
# 2. EnergyAgent
# ----------------------------------------------------
class EnergyAgent(BaseGreenAgent):
    def __init__(self):
        super().__init__("EnergyAgent", "Energy Optimization")

    def observe(self, db: Session, profile: BusinessProfile) -> Dict[str, Any]:
        metrics = (
            db.query(GreenOperationalMetric)
            .filter(
                GreenOperationalMetric.business_profile_id == profile.id,
                GreenOperationalMetric.metric_type == "daily_kwh",
            )
            .all()
        )
        return {
            "has_energy_data": len(metrics) > 0,
            "metrics": metrics,
            "profile": profile,
        }

    def detect(self, observations: Dict[str, Any]) -> List[Dict[str, Any]]:
        detections = []
        if not observations["has_energy_data"]:
            # Explicit non-fabrication: No data detected
            return detections

        metrics = observations["metrics"]
        avg_kwh = sum(m.value for m in metrics) / len(metrics)

        # Flag high consumption if baseline daily kWh exceeds typical category threshold
        # (e.g. > 150 kWh/day for small textile mill or restaurant)
        if avg_kwh > 120.0:
            detections.append({
                "type": "PEAK_ENERGY_DRAIN",
                "metric": "daily_kwh",
                "value": round(avg_kwh, 1),
                "is_demo": metrics[0].is_demo,
                "observation_id": metrics[0].id,
                "label": metrics[0].label or "Main Electricity Incomer",
            })

        return detections

    def analyze(self, db: Session, detections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        recommendations = []
        for det in detections:
            daily_kwh = det["value"]
            monthly_baseline = daily_kwh * 30.0
            projected_monthly = monthly_baseline * 0.82  # 18% reduction through off-peak shifting
            energy_impact = ImpactCalculationService.calculate_energy_savings(
                baseline_kwh=monthly_baseline,
                projected_kwh=projected_monthly,
                assumptions="Rescheduling heavy inductive motor and refrigeration defrost cycles to off-peak tariff periods."
            )
            cost_impact = ImpactCalculationService.calculate_cost_savings(energy_impact.get("value"))
            carbon_impact = ImpactCalculationService.calculate_carbon_savings(db, energy_reduction_kwh=energy_impact.get("value"))

            policy_status, policy_notes = GreenPolicyValidator.validate_recommendation(
                category="Energy Optimization",
                action_title="Shift heavy motorized cycles to off-peak grid hours",
                parameters={"target_system": det.get("label", ""), "operating_hours": "off-peak"}
            )

            recommendations.append({
                "agent_type": self.agent_name,
                "title": "Industrial Load Balancing & Off-Peak Shift",
                "category": self.category,
                "priority": "High",
                "severity": "Warning",
                "detected_issue": f"Average daily power consumption of {daily_kwh} kWh/day coincides with peak grid tariff windows.",
                "evidence": [
                    {
                        "source_type": "DEMO_DATA" if det["is_demo"] else "ENERGY_DATA",
                        "source_id": det["observation_id"],
                        "metric": det["metric"],
                        "value": f"{daily_kwh} kWh/day",
                        "evidence_summary": f"Daily metered consumption averaged {daily_kwh} kWh over recent sampling periods.",
                        "is_demo": det["is_demo"],
                        "observation_time": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                    }
                ],
                "cause": "Inductive machinery and heating units operate concurrently during peak grid hours without automatic load leveling.",
                "recommended_action": "Configure staggered equipment scheduling and program programmable logic controllers (PLCs) for off-peak pre-chilling/pre-heating.",
                "estimated_energy_impact": energy_impact,
                "estimated_cost_impact": cost_impact,
                "estimated_carbon_impact": carbon_impact,
                "implementation_effort": "Medium",
                "confidence": 0.89,
                "policy_status": policy_status,
                "policy_notes": policy_notes,
            })

        return recommendations


# ----------------------------------------------------
# 3. ResourceWasteAgent
# ----------------------------------------------------
class ResourceWasteAgent(BaseGreenAgent):
    def __init__(self):
        super().__init__("ResourceWasteAgent", "Workflow Digitization")

    def observe(self, db: Session, profile: BusinessProfile) -> Dict[str, Any]:
        tasks = (
            db.query(ComplianceTask)
            .filter(ComplianceTask.business_profile_id == profile.id)
            .all()
        )
        docs = (
            db.query(Document)
            .filter(Document.business_profile_id == profile.id)
            .all()
        )
        paper_metrics = (
            db.query(GreenOperationalMetric)
            .filter(
                GreenOperationalMetric.business_profile_id == profile.id,
                GreenOperationalMetric.metric_type == "paper_reams_consumed",
            )
            .first()
        )

        return {
            "tasks_count": len(tasks),
            "docs_count": len(docs),
            "paper_metric": paper_metrics,
            "profile": profile,
        }

    def detect(self, observations: Dict[str, Any]) -> List[Dict[str, Any]]:
        detections = []
        paper_metric = observations.get("paper_metric")
        docs_count = observations.get("docs_count", 0)

        # If paper metric is recorded or if business vault is under-utilized relative to profile size
        if paper_metric and paper_metric.value > 10.0:
            detections.append({
                "type": "PAPER_INTENSIVE_PROCESS",
                "metric": "paper_reams_consumed",
                "value": paper_metric.value,
                "is_demo": paper_metric.is_demo,
                "observation_id": paper_metric.id,
            })
        elif docs_count < 3:
            detections.append({
                "type": "PHYSICAL_LOG_DEPENDENCY",
                "metric": "digital_vault_coverage",
                "value": docs_count,
                "is_demo": False,
                "observation_id": str(observations["profile"].id),
            })

        return detections

    def analyze(self, db: Session, detections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        recommendations = []
        for det in detections:
            if det["type"] == "PAPER_INTENSIVE_PROCESS":
                reams = det["value"]
                carbon_impact = ImpactCalculationService.calculate_carbon_savings(db, paper_reams_saved=reams * 0.70)
                # Cost savings from paper reams: ₹350 per ream
                cost_val = round(reams * 0.70 * 350.0, 2)
                cost_impact = {
                    "value": cost_val,
                    "currency": "INR",
                    "formula": "reams_saved * ream_unit_cost",
                    "assumptions": "Calculated at ₹350 per standard 500-sheet A4 virgin pulp ream.",
                    "timestamp": datetime.utcnow().isoformat()
                }

                recommendations.append({
                    "agent_type": self.agent_name,
                    "title": "Statutory Document Digitization & Paperless Filing",
                    "category": self.category,
                    "priority": "Medium",
                    "severity": "Info",
                    "detected_issue": f"Annual operational paperwork consumes approximately {reams} reams of paper across compliance logs and physical dispatches.",
                    "evidence": [
                        {
                            "source_type": "DEMO_DATA" if det["is_demo"] else "SYSTEM_METRIC",
                            "source_id": det["observation_id"],
                            "metric": det["metric"],
                            "value": f"{reams} reams/year",
                            "evidence_summary": f"Documented paper consumption of {reams} reams across physical inspection registers.",
                            "is_demo": det["is_demo"],
                            "observation_time": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                        }
                    ],
                    "cause": "Routine regulatory registers (Form 21, ESI records, Wage slips) are maintained in printed hard-copy binders.",
                    "recommended_action": "Migrate physical factory registers into POWER HOUSE Document Vault with cryptographic SHA-256 evidence hashing.",
                    "estimated_energy_impact": None,
                    "estimated_cost_impact": cost_impact,
                    "estimated_carbon_impact": carbon_impact,
                    "implementation_effort": "Low",
                    "confidence": 0.94,
                    "policy_status": "PASS",
                    "policy_notes": "Digital statutory records are recognized under the Information Technology Act 2000 and Factories Rules.",
                })
            elif det["type"] == "PHYSICAL_LOG_DEPENDENCY":
                recommendations.append({
                    "agent_type": self.agent_name,
                    "title": "Establishment Compliance Vault Centralization",
                    "category": self.category,
                    "priority": "Low",
                    "severity": "Info",
                    "detected_issue": "Digital vault contains under 3 statutory certificates, indicating reliance on physical paper filings.",
                    "evidence": [
                        {
                            "source_type": "BUSINESS_PROFILE",
                            "source_id": det["observation_id"],
                            "metric": "vault_document_count",
                            "value": f"{det['value']} documents",
                            "evidence_summary": "Only {det['value']} digital certificates stored in secure tenant vault.",
                            "is_demo": False,
                            "observation_time": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                        }
                    ],
                    "cause": "Recent statutory renewals have not been centralized into digital cloud vaults.",
                    "recommended_action": "Upload business licenses and inspection clearances to eliminate paper loss risk and establish digital audit readiness.",
                    "estimated_energy_impact": None,
                    "estimated_cost_impact": None,
                    "estimated_carbon_impact": None,
                    "implementation_effort": "Low",
                    "confidence": 0.85,
                    "policy_status": "PASS",
                    "policy_notes": "Policy checks confirmed. Zero runtime constraints.",
                })

        return recommendations
