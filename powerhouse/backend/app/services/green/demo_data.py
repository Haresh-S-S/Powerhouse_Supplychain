import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.green_metric import GreenOperationalMetric


def seed_demo_operational_metrics(db: Session, business_profile_id: str) -> None:
    """
    Seeds a safe development-only synthetic operational dataset for the active business profile.
    All records are strictly marked: is_demo=True, with explicit '[DEMO DATA]' prefixes in labels.
    Never mixed with unmonitored production profiles.
    """
    # Clear existing demo metrics for this profile to prevent duplication
    db.query(GreenOperationalMetric).filter(
        GreenOperationalMetric.business_profile_id == business_profile_id,
        GreenOperationalMetric.is_demo == True,
    ).delete()

    synthetic_records = [
        {
            "metric_type": "cpu_utilization",
            "value": 18.4,
            "unit": "%",
            "label": "[DEMO DATA] Cloud Compute Cluster Node-01 (Idle Average)",
        },
        {
            "metric_type": "idle_compute_hours",
            "value": 54.0,
            "unit": "hours/week",
            "label": "[DEMO DATA] Off-Shift Inactive Worker Compute Hours",
        },
        {
            "metric_type": "redundant_inference_pct",
            "value": 42.0,
            "unit": "%",
            "label": "[DEMO DATA] Uncached Regulatory Advisory Query Cache Misses",
        },
        {
            "metric_type": "daily_kwh",
            "value": 168.5,
            "unit": "kWh/day",
            "label": "[DEMO DATA] Main Factory Substation Smart Meter Feeder-A",
        },
        {
            "metric_type": "paper_reams_consumed",
            "value": 14.0,
            "unit": "reams/year",
            "label": "[DEMO DATA] Annual Printed Regulatory Ledger & Dispatch Forms",
        },
    ]

    for rec in synthetic_records:
        metric = GreenOperationalMetric(
            id=str(uuid.uuid4()),
            business_profile_id=business_profile_id,
            metric_type=rec["metric_type"],
            value=rec["value"],
            unit=rec["unit"],
            is_demo=True,
            label=rec["label"],
            collected_at=datetime.utcnow(),
        )
        db.add(metric)

    db.commit()
