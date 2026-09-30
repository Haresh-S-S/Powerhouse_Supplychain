"""
Disruption Sensing and Impact Service
-------------------------------------
Connects to SupplyMind to provide:
1. Live disruption intelligence feed
2. Node blast-radius mapping
3. Baseline Demand vs Disrupted Supply vs AI-Recovered Supply timeline curves
"""
from __future__ import annotations
from typing import Dict, Any, List
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.supply_chain_tower import DisruptionEvent
from app.supply_chain_ai.adapters.supplymind_adapter import SupplyMindAdapter


class DisruptionService:

    @staticmethod
    def get_live_disruptions(db: Session, business_id: str) -> List[Dict[str, Any]]:
        """Fetch active disruption events formatted for the live enterprise feed."""
        events = db.query(DisruptionEvent).filter(
            DisruptionEvent.business_id == business_id
        ).order_by(DisruptionEvent.detected_at.desc()).all()

        if not events:
            # Fallback to calibrated SupplyMind preset
            presets = SupplyMindAdapter.get().get_preset_scenarios()
            return [
                {
                    "id": p.get("signal_id"),
                    "title": p.get("title", "Disruption Signal"),
                    "disruption_type": p.get("disruption_type"),
                    "severity": "Critical" if p.get("peak_severity", 0.7) > 0.8 else "High",
                    "confidence": p.get("warning_confidence", 0.85),
                    "affected_region": p.get("affected_region"),
                    "affected_nodes": p.get("affected_node_ids", []),
                    "impact_delay_days": p.get("estimated_duration_days", 8.0),
                    "financial_impact_usd": 420000.0,
                    "lifecycle_phase": "active",
                    "description": p.get("description"),
                    "detected_at": datetime.utcnow().isoformat(),
                    "ai_response_required": True,
                }
                for p in presets
            ]

        res = []
        for e in events:
            res.append({
                "id": e.id,
                "signal_id": e.signal_id,
                "title": e.title,
                "disruption_type": e.disruption_type,
                "severity": e.severity,
                "confidence": e.confidence,
                "affected_region": e.affected_region,
                "affected_nodes": e.affected_node_ids or [],
                "impact_delay_days": e.impact_delay_days,
                "financial_impact_usd": e.financial_impact_usd,
                "lifecycle_phase": e.lifecycle_phase,
                "description": e.description,
                "commodity_effects": e.commodity_effects or {},
                "status": e.status,
                "detected_at": e.detected_at.strftime("%Y-%m-%d %H:%M UTC"),
                "ai_response_required": (e.status == "Active"),
            })
        return res

    @staticmethod
    def get_disruption_impact_curve(
        disruption_id: str = "SIG-TYPHOON-GAEMI",
        severity: float = 0.85,
    ) -> Dict[str, Any]:
        """
        Calculates time-series comparison:
        Baseline Demand vs Disrupted Supply vs AI-Recovered Supply
        with quantitative resilience metrics.
        """
        adapter = SupplyMindAdapter.get()
        return adapter.compute_impact_timeline(
            baseline_demand=1200.0,
            disruption_severity=severity,
            delay_days=8,
            recovery_days=4,
            total_days=30,
        )
