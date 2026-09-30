"""
Logistics Routing & OR-Tools Optimization Service
-------------------------------------------------
Provides:
1. OR-Tools route optimization avoiding disrupted corridors
2. Visual route comparison: Original vs AI Reroute
3. Route list and shipment tracking
"""
from __future__ import annotations
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from app.models.supply_chain_tower import SupplyRoute, SupplyShipment
from app.supply_chain_ai.adapters.ortools_routing_adapter import OrToolsRoutingAdapter


class LogisticsService:

    @staticmethod
    def get_routes(db: Session, business_id: str) -> List[Dict[str, Any]]:
        """List all active supply routes with status and risk ratings."""
        routes = db.query(SupplyRoute).filter(SupplyRoute.business_id == business_id).all()
        res = []
        for r in routes:
            res.append({
                "id": r.id,
                "code": r.route_code,
                "name": r.name,
                "origin": r.origin_name,
                "destination": r.destination_name,
                "waypoints": r.waypoints or [],
                "distance_km": r.distance_km,
                "transit_time_days": r.transit_time_days,
                "cost_usd": r.cost_usd,
                "co2_kg": r.co2_kg,
                "primary_mode": r.primary_mode,
                "status": r.status,  # Normal, Disrupted, Congested, Alternate
                "risk_level": r.risk_level,
            })
        return res

    @staticmethod
    def get_route_comparison(
        origin: str = "Taiwan Strait (TSMC Hsinchu)",
        destination: str = "DC South (Dallas Regional)",
        blocked_node: str = "Port of Kaohsiung",
    ) -> Dict[str, Any]:
        """
        Run OR-Tools optimization to compute detailed route comparison:
        Original Route vs Disrupted Segment vs AI Reroute.
        """
        adapter = OrToolsRoutingAdapter.get()
        return adapter.optimize_reroute(
            origin=origin,
            destination=destination,
            blocked_nodes=[blocked_node],
        )

    @staticmethod
    def get_shipments(db: Session, business_id: str, limit: int = 30) -> List[Dict[str, Any]]:
        """List active tracked shipments."""
        shipments = db.query(SupplyShipment).filter(
            SupplyShipment.business_id == business_id
        ).limit(limit).all()

        res = []
        for sh in shipments:
            res.append({
                "id": sh.id,
                "tracking_number": sh.tracking_number,
                "cargo_description": sh.cargo_description,
                "cargo_value_usd": sh.cargo_value_usd,
                "origin": sh.origin,
                "destination": sh.destination,
                "current_location": sh.current_location,
                "eta_days": sh.eta_days,
                "delay_hours": sh.delay_hours,
                "status": sh.status,  # In Transit, Delayed, Rerouted, Delivered
            })
        return res
