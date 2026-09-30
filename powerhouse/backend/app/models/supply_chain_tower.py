import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base


class Warehouse(Base):
    __tablename__ = "supply_warehouses"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    business_id = Column(String(36), ForeignKey("business_profiles.id", ondelete="CASCADE"), nullable=False, index=True)

    code = Column(String(50), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    warehouse_type = Column(String(100), nullable=False, default="Distribution Center")  # Distribution Center, Regional Hub, Factory Store, Port Warehouse
    location = Column(String(100), nullable=False)
    country = Column(String(100), nullable=False, default="United States")
    lat = Column(Float, nullable=True)
    lng = Column(Float, nullable=True)
    capacity_units = Column(Integer, nullable=False, default=50000)
    utilized_units = Column(Integer, nullable=False, default=32000)
    operating_cost_per_day = Column(Float, nullable=False, default=1250.0)
    status = Column(String(50), nullable=False, default="Operational")  # Operational, Warning, Critical, Maintenance
    is_demo = Column(Boolean, nullable=False, default=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    business_profile = relationship("BusinessProfile")
    inventory_records = relationship("InventoryRecord", back_populates="warehouse", cascade="all, delete-orphan")


class InventoryRecord(Base):
    __tablename__ = "supply_inventory_records"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    business_id = Column(String(36), ForeignKey("business_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    warehouse_id = Column(String(36), ForeignKey("supply_warehouses.id", ondelete="CASCADE"), nullable=False, index=True)
    supply_item_id = Column(String(36), ForeignKey("supply_items.id", ondelete="SET NULL"), nullable=True, index=True)

    sku = Column(String(100), nullable=False, index=True)
    item_name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False, default="Semiconductors")
    on_hand = Column(Float, nullable=False, default=0.0)
    allocated = Column(Float, nullable=False, default=0.0)
    on_order = Column(Float, nullable=False, default=0.0)
    safety_stock = Column(Float, nullable=False, default=1000.0)
    reorder_point = Column(Float, nullable=False, default=1500.0)
    unit_cost = Column(Float, nullable=False, default=10.0)
    holding_cost_rate = Column(Float, nullable=False, default=0.18)
    lead_time_days = Column(Integer, nullable=False, default=14)
    forecast_demand_30d = Column(Float, nullable=False, default=1200.0)
    shortfall = Column(Float, nullable=False, default=0.0)
    status = Column(String(50), nullable=False, default="Healthy")  # Healthy, Warning, Critical, Overstocked
    is_demo = Column(Boolean, nullable=False, default=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    business_profile = relationship("BusinessProfile")
    warehouse = relationship("Warehouse", back_populates="inventory_records")
    supply_item = relationship("SupplyItem")


class SupplyRoute(Base):
    __tablename__ = "supply_routes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    business_id = Column(String(36), ForeignKey("business_profiles.id", ondelete="CASCADE"), nullable=False, index=True)

    route_code = Column(String(50), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    origin_type = Column(String(50), nullable=False)  # Supplier, Port, Warehouse
    origin_name = Column(String(100), nullable=False)
    destination_type = Column(String(50), nullable=False)  # Port, DC, Factory
    destination_name = Column(String(100), nullable=False)
    waypoints = Column(JSON, nullable=False, default=list)  # list of waypoints / transit hubs
    distance_km = Column(Float, nullable=False, default=1200.0)
    transit_time_days = Column(Float, nullable=False, default=4.5)
    cost_usd = Column(Float, nullable=False, default=4500.0)
    co2_kg = Column(Float, nullable=False, default=850.0)
    primary_mode = Column(String(50), nullable=False, default="Maritime")  # Maritime, Air, Road, Rail, Multimodal
    status = Column(String(50), nullable=False, default="Normal")  # Normal, Disrupted, Congested, Alternate
    risk_level = Column(String(50), nullable=False, default="Low")  # Low, Medium, High, Critical
    is_demo = Column(Boolean, nullable=False, default=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    business_profile = relationship("BusinessProfile")
    shipments = relationship("SupplyShipment", back_populates="route")


class SupplyShipment(Base):
    __tablename__ = "supply_shipments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    business_id = Column(String(36), ForeignKey("business_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    route_id = Column(String(36), ForeignKey("supply_routes.id", ondelete="SET NULL"), nullable=True, index=True)

    tracking_number = Column(String(100), nullable=False, index=True)
    cargo_description = Column(String(255), nullable=False)
    cargo_value_usd = Column(Float, nullable=False, default=50000.0)
    origin = Column(String(100), nullable=False)
    destination = Column(String(100), nullable=False)
    current_location = Column(String(100), nullable=False)
    eta_days = Column(Float, nullable=False, default=3.0)
    delay_hours = Column(Float, nullable=False, default=0.0)
    status = Column(String(50), nullable=False, default="In Transit")  # In Transit, Delayed, Rerouted, Delivered
    is_demo = Column(Boolean, nullable=False, default=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    business_profile = relationship("BusinessProfile")
    route = relationship("SupplyRoute", back_populates="shipments")


class DisruptionEvent(Base):
    __tablename__ = "supply_disruptions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    business_id = Column(String(36), ForeignKey("business_profiles.id", ondelete="CASCADE"), nullable=False, index=True)

    signal_id = Column(String(100), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    disruption_type = Column(String(100), nullable=False)  # cyclone, port_congestion, supplier_outage, tariff_increase, geopolitical, labor_strike, severe_weather
    severity = Column(String(50), nullable=False, default="High")  # Low, Medium, High, Critical
    confidence = Column(Float, nullable=False, default=0.85)
    affected_region = Column(String(100), nullable=False)
    affected_node_ids = Column(JSON, nullable=False, default=list)
    impact_delay_days = Column(Float, nullable=False, default=7.0)
    financial_impact_usd = Column(Float, nullable=False, default=250000.0)
    lifecycle_phase = Column(String(50), nullable=False, default="active")  # warning, active, recovery, resolved
    description = Column(Text, nullable=False)
    commodity_effects = Column(JSON, nullable=False, default=dict)
    status = Column(String(50), nullable=False, default="Active")  # Active, Mitigated, Monitoring, Resolved
    detected_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_demo = Column(Boolean, nullable=False, default=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    business_profile = relationship("BusinessProfile")
    recommendations = relationship("AIRecommendation", back_populates="disruption")


class SupplyScenario(Base):
    __tablename__ = "supply_scenarios"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    business_id = Column(String(36), ForeignKey("business_profiles.id", ondelete="CASCADE"), nullable=False, index=True)

    name = Column(String(255), nullable=False)
    scenario_type = Column(String(100), nullable=False)  # port_closure, supplier_failure, tariff_increase, severe_weather, custom
    parameters = Column(JSON, nullable=False, default=dict)
    status = Column(String(50), nullable=False, default="Simulated")
    is_demo = Column(Boolean, nullable=False, default=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    business_profile = relationship("BusinessProfile")
    results = relationship("SupplyScenarioResult", back_populates="scenario", cascade="all, delete-orphan")


class SupplyScenarioResult(Base):
    __tablename__ = "supply_scenario_results"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    scenario_id = Column(String(36), ForeignKey("supply_scenarios.id", ondelete="CASCADE"), nullable=False, index=True)
    business_id = Column(String(36), ForeignKey("business_profiles.id", ondelete="CASCADE"), nullable=False, index=True)

    # Baseline vs Scenario vs AI Response metrics
    cost_impact_pct = Column(Float, nullable=False, default=18.0)
    delay_impact_days = Column(Float, nullable=False, default=11.0)
    scenario_risk_score = Column(Float, nullable=False, default=72.0)
    scenario_recovery_days = Column(Float, nullable=False, default=16.0)

    ai_cost_impact_pct = Column(Float, nullable=False, default=8.0)
    ai_delay_days = Column(Float, nullable=False, default=4.0)
    ai_risk_score = Column(Float, nullable=False, default=31.0)
    ai_recovery_days = Column(Float, nullable=False, default=6.0)

    comparison_data = Column(JSON, nullable=False, default=dict)
    ai_summary = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    scenario = relationship("SupplyScenario", back_populates="results")
    business_profile = relationship("BusinessProfile")


class AIRecommendation(Base):
    __tablename__ = "supply_ai_recommendations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    business_id = Column(String(36), ForeignKey("business_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    disruption_id = Column(String(36), ForeignKey("supply_disruptions.id", ondelete="SET NULL"), nullable=True, index=True)

    title = Column(String(255), nullable=False)
    recommendation_type = Column(String(100), nullable=False)  # reroute_shipment, rebalance_inventory, activate_backup_supplier, increase_safety_stock
    description = Column(Text, nullable=False)
    expected_cost_usd = Column(Float, nullable=False, default=0.0)
    expected_delay_reduction_days = Column(Float, nullable=False, default=0.0)
    expected_risk_reduction_pct = Column(Float, nullable=False, default=0.0)
    requires_human_approval = Column(Boolean, nullable=False, default=True)
    approval_status = Column(String(50), nullable=False, default="PENDING")  # PENDING, APPROVED, REJECTED
    approved_by = Column(String(100), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    explanation_why = Column(Text, nullable=False)
    action_payload = Column(JSON, nullable=False, default=dict)
    is_demo = Column(Boolean, nullable=False, default=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    business_profile = relationship("BusinessProfile")
    disruption = relationship("DisruptionEvent", back_populates="recommendations")


class SupplyChainAudit(Base):
    __tablename__ = "supply_chain_audits"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    business_id = Column(String(36), ForeignKey("business_profiles.id", ondelete="CASCADE"), nullable=False, index=True)

    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    agent_name = Column(String(100), nullable=False)  # Disruption Agent, Scenario Agent, Logistics Agent, Inventory Agent, Human Approval Gate
    action = Column(String(255), nullable=False)
    reason = Column(Text, nullable=False)
    data_used = Column(JSON, nullable=False, default=dict)
    risk_level = Column(String(50), nullable=False, default="Medium")
    approval_required = Column(Boolean, nullable=False, default=False)
    decision = Column(String(100), nullable=False, default="RECOMMENDED")
    is_demo = Column(Boolean, nullable=False, default=False)

    # Relationships
    business_profile = relationship("BusinessProfile")
