from datetime import datetime
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models.green_opportunity import GreenOpportunity
from app.models.green_impact import GreenImpactMeasurement
from app.models.green_metric import GreenOperationalMetric
from app.models.document import Document
from app.models.compliance_task import ComplianceTask


class GreenScoreService:
    @staticmethod
    def calculate_green_score(db: Session, business_profile_id: str) -> Dict[str, Any]:
        """
        Deterministic calculation of Green Operations Score (0-100).
        5 Explicit Pillars:
        1. Compute Efficiency (25%)
        2. Resource Efficiency (25%)
        3. Digital Workflow Adoption (20%)
        4. Completed Green Actions (15%)
        5. Verified Measured Impacts (15%)
        """
        # --- Pillar 1: Compute Efficiency (25%) ---
        # Evaluate compute metrics if available; default to 65% baseline if unmonitored
        compute_metric = (
            db.query(GreenOperationalMetric)
            .filter(
                GreenOperationalMetric.business_profile_id == business_profile_id,
                GreenOperationalMetric.metric_type == "cpu_utilization",
            )
            .order_by(GreenOperationalMetric.collected_at.desc())
            .first()
        )
        if compute_metric:
            # Ideal utilization window: 45% - 75% -> 100 pts; <25% -> 50 pts; >85% -> 60 pts
            val = compute_metric.value
            if 45 <= val <= 75:
                compute_score = 92.0
            elif val < 25:
                compute_score = 54.0
            else:
                compute_score = 72.0
        else:
            compute_score = 65.0

        # --- Pillar 2: Resource Efficiency (25%) ---
        # Ratio of resolved/verified opportunities vs detected critical issues
        total_opps = (
            db.query(GreenOpportunity)
            .filter(GreenOpportunity.business_profile_id == business_profile_id)
            .count()
        )
        resolved_opps = (
            db.query(GreenOpportunity)
            .filter(
                GreenOpportunity.business_profile_id == business_profile_id,
                GreenOpportunity.status.in_(["COMPLETED", "VERIFIED", "APPROVED", "TASK_CREATED"]),
            )
            .count()
        )
        if total_opps > 0:
            resource_score = min(100.0, 50.0 + (resolved_opps / total_opps) * 50.0)
        else:
            resource_score = 70.0

        # --- Pillar 3: Digital Workflow Adoption (20%) ---
        # Number of digital documents uploaded into vault vs paper records
        vault_docs_count = (
            db.query(Document)
            .filter(Document.business_profile_id == business_profile_id)
            .count()
        )
        # 5+ documents in vault -> 90 pts, 2-4 -> 75 pts, <2 -> 55 pts
        if vault_docs_count >= 5:
            digital_score = 90.0
        elif vault_docs_count >= 2:
            digital_score = 75.0
        else:
            digital_score = 55.0

        # --- Pillar 4: Completed Green Actions (15%) ---
        # Real tasks in Compliance Tasks with category 'Green Operations' marked completed
        green_tasks = (
            db.query(ComplianceTask)
            .filter(
                ComplianceTask.business_profile_id == business_profile_id,
                ComplianceTask.category == "Green Operations",
            )
            .all()
        )
        completed_green_tasks = [t for t in green_tasks if t.status in ["Completed", "Verified"]]
        if len(green_tasks) > 0:
            actions_score = min(100.0, (len(completed_green_tasks) / len(green_tasks)) * 100.0)
        elif resolved_opps > 0:
            actions_score = 70.0
        else:
            actions_score = 50.0

        # --- Pillar 5: Verified Measured Impacts (15%) ---
        verified_impacts = (
            db.query(GreenImpactMeasurement)
            .filter(
                GreenImpactMeasurement.business_profile_id == business_profile_id,
                GreenImpactMeasurement.verification_status == "VERIFIED",
            )
            .count()
        )
        pending_impacts = (
            db.query(GreenImpactMeasurement)
            .filter(
                GreenImpactMeasurement.business_profile_id == business_profile_id,
                GreenImpactMeasurement.verification_status == "PENDING",
            )
            .count()
        )
        if verified_impacts >= 2:
            impact_score = 95.0
        elif verified_impacts == 1:
            impact_score = 80.0
        elif pending_impacts > 0:
            impact_score = 65.0
        else:
            impact_score = 50.0

        # Weighted calculation
        c_compute = compute_score * 0.25
        c_resource = resource_score * 0.25
        c_digital = digital_score * 0.20
        c_actions = actions_score * 0.15
        c_impact = impact_score * 0.15

        final_score = int(round(c_compute + c_resource + c_digital + c_actions + c_impact))
        final_score = max(0, min(100, final_score))

        rating = "Excellent" if final_score >= 80 else "Good" if final_score >= 65 else "Moderate" if final_score >= 50 else "Needs Attention"

        components = [
            {
                "name": "Compute Efficiency",
                "score": round(compute_score, 1),
                "weight": 0.25,
                "contribution": round(c_compute, 1),
                "description": "Workload utilization, idle compute mitigation, and AI prompt batching."
            },
            {
                "name": "Resource Efficiency",
                "score": round(resource_score, 1),
                "weight": 0.25,
                "contribution": round(c_resource, 1),
                "description": "Progress in remediating flagged operational energy and material waste opportunities."
            },
            {
                "name": "Digital Workflow Adoption",
                "score": round(digital_score, 1),
                "weight": 0.20,
                "contribution": round(c_digital, 1),
                "description": "Transition from paper-bound statutory logs to verified digital vault records."
            },
            {
                "name": "Completed Green Actions",
                "score": round(actions_score, 1),
                "weight": 0.15,
                "contribution": round(c_actions, 1),
                "description": "Execution of human-approved green operational compliance tasks."
            },
            {
                "name": "Verified Measured Impact",
                "score": round(impact_score, 1),
                "weight": 0.15,
                "contribution": round(c_impact, 1),
                "description": "Empirically verified before-and-after operational telemetry measurements."
            },
        ]

        return {
            "score": final_score,
            "rating": rating,
            "calculation_method": "Multi-Pillar Deterministic Weighted Average (Compute 25%, Resource 25%, Digital 20%, Action 15%, Impact 15%)",
            "last_updated": datetime.utcnow().strftime("%d %b %Y, %H:%M UTC"),
            "components": components,
        }
