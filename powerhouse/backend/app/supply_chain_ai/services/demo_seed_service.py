"""
Supply Chain Control Tower Demo Seed Service
--------------------------------------------
Seeds a consistent, interconnected, and realistic enterprise dataset:
- 12 suppliers (TSMC, Samsung, Foxconn, Bosch, etc.)
- 5 ports (Kaohsiung, Shanghai, Rotterdam, Los Angeles, Mumbai)
- 4 distribution centers / warehouses (DC North, DC South, DC West, DC Central)
- 3 factories (Austin GigaFab, Munich Assembly, Pune Plant)
- 20 SKUs (DRAM, MCUs, MOSFETs, Lithium Cells, etc.)
- 15 intermodal routes
- 30 shipments
- 3 active disruptions
- AI recommendations awaiting human approval
- Agent audit trail
"""
from __future__ import annotations
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from app.models.business import BusinessProfile
from app.models.supplier import Supplier, SupplierDocument, SupplyItem, SupplyChainRisk
from app.models.supply_chain_tower import (
    Warehouse,
    InventoryRecord,
    SupplyRoute,
    SupplyShipment,
    DisruptionEvent,
    SupplyScenario,
    SupplyScenarioResult,
    AIRecommendation,
    SupplyChainAudit,
)


def seed_resilient_control_tower_data(db: Session, business_id: str) -> Dict[str, Any]:
    """Seed complete, consistent supply chain data for the control tower."""
    # First cleanup any previous demo records for this business
    cleanup_control_tower_demo_data(db, business_id)

    # 1. Warehouses (4 major distribution hubs)
    warehouses_data = [
        {"code": "DC-NORTH", "name": "DC North (Hamburg Hub)", "type": "Distribution Center", "location": "Hamburg", "country": "Germany", "lat": 53.55, "lng": 9.99, "cap": 60000, "util": 38000, "cost": 1400.0, "status": "Operational"},
        {"code": "DC-SOUTH", "name": "DC South (Dallas Regional)", "type": "Distribution Center", "location": "Dallas, TX", "country": "United States", "lat": 32.77, "lng": -96.79, "cap": 75000, "util": 58000, "cost": 1850.0, "status": "Warning"},
        {"code": "DC-WEST", "name": "DC West (Tokyo Hub)", "type": "Distribution Center", "location": "Tokyo", "country": "Japan", "lat": 35.67, "lng": 139.65, "cap": 50000, "util": 29000, "cost": 1300.0, "status": "Operational"},
        {"code": "DC-CENTRAL", "name": "DC Central (Mumbai Logistics)", "type": "Regional Hub", "location": "Navi Mumbai", "country": "India", "lat": 19.03, "lng": 73.02, "cap": 45000, "util": 31000, "cost": 950.0, "status": "Operational"},
    ]
    warehouse_objs = {}
    for wd in warehouses_data:
        w = Warehouse(
            business_id=business_id,
            code=wd["code"],
            name=wd["name"],
            warehouse_type=wd["type"],
            location=wd["location"],
            country=wd["country"],
            lat=wd["lat"],
            lng=wd["lng"],
            capacity_units=wd["cap"],
            utilized_units=wd["util"],
            operating_cost_per_day=wd["cost"],
            status=wd["status"],
            is_demo=True,
        )
        db.add(w)
        db.flush()
        warehouse_objs[wd["code"]] = w

    # 2. Suppliers (12 enterprise suppliers)
    suppliers_data = [
        {"name": "TSMC Fab 14", "type": "Component", "loc": "Tainan Science Park", "country": "Taiwan", "lead": 28, "dep": 85.0, "risk": "Critical", "prods": ["3nm/5nm FinFET Wafers", "Microcontroller ICs", "Automotive Silicon"]},
        {"name": "Foxconn Precision", "type": "Component", "loc": "Shenzhen", "country": "China", "lead": 22, "dep": 70.0, "risk": "High", "prods": ["PCB Assemblies", "Display Connectors", "Power Bricks"]},
        {"name": "Bosch Mobility Electronics", "type": "Component", "loc": "Stuttgart", "country": "Germany", "lead": 12, "dep": 45.0, "risk": "Low", "prods": ["CAN Bus Controllers", "Engine Control Units", "Radar Sensors"]},
        {"name": "Samsung Electronics", "type": "Component", "loc": "Hwaseong", "country": "South Korea", "lead": 16, "dep": 60.0, "risk": "Medium", "prods": ["DRAM-16GB-DDR5", "NAND Flash", "Mobile SoCs"]},
        {"name": "Murata Manufacturing", "type": "Component", "loc": "Kyoto", "country": "Japan", "lead": 14, "dep": 35.0, "risk": "Low", "prods": ["MLCC Capacitors", "Ceramic Resonators", "RF Filters"]},
        {"name": "TDK Electronics", "type": "Component", "loc": "Tokyo", "country": "Japan", "lead": 15, "dep": 30.0, "risk": "Low", "prods": ["Power Inductors", "Ferrite Beads", "EMC Filters"]},
        {"name": "Tata AutoComp Systems", "type": "Component", "loc": "Pune", "country": "India", "lead": 10, "dep": 40.0, "risk": "Medium", "prods": ["Wiring Harnesses", "Thermal Management Units", "Battery Trays"]},
        {"name": "STMicroelectronics", "type": "Component", "loc": "Grenoble", "country": "France", "lead": 18, "dep": 25.0, "risk": "Low", "prods": ["SiC Power MOSFETs", "STM32 Microcontrollers", "MEMS Sensors"]},
        {"name": "Infineon Technologies", "type": "Component", "loc": "Dresden", "country": "Germany", "lead": 14, "dep": 30.0, "risk": "Low", "prods": ["IGBT Power Modules", "Gate Drivers", "Secured Microcontrollers"]},
        {"name": "SK Hynix", "type": "Component", "loc": "Icheon", "country": "South Korea", "lead": 17, "dep": 50.0, "risk": "Medium", "prods": ["High Bandwidth Memory (HBM3)", "DDR5 Modules", "LPDDR5X"]},
        {"name": "Texas Instruments", "type": "Component", "loc": "Dallas, TX", "country": "United States", "lead": 8, "dep": 35.0, "risk": "Low", "prods": ["Analog Amplifiers", "Buck Converters", "Voltage Regulators"]},
        {"name": "Renesas Electronics", "type": "Component", "loc": "Tokyo", "country": "Japan", "lead": 20, "dep": 40.0, "risk": "Medium", "prods": ["Automotive MCUs", "Timing ICs", "Power PMICs"]},
    ]
    supplier_objs = {}
    for sd in suppliers_data:
        s = Supplier(
            business_id=business_id,
            name=sd["name"],
            supplier_type=sd["type"],
            location=sd["loc"],
            country=sd["country"],
            lead_time_days=sd["lead"],
            dependency_percentage=sd["dep"],
            risk_status=sd["risk"],
            products_or_materials=sd["prods"],
            status="Active",
            is_demo=True,
        )
        db.add(s)
        db.flush()
        supplier_objs[sd["name"]] = s

        # Add Compliance Document
        doc = SupplierDocument(
            supplier_id=s.id,
            document_name=f"ISO 9001 & Quality Certification - {s.name}",
            document_type="ISO 9001",
            verification_status="Verified" if sd["risk"] != "Critical" else "Pending",
            expiry_date="2027-12-31",
        )
        db.add(doc)

    # 3. Supply Items & Inventory Records (20 SKUs)
    skus_data = [
        {"sku": "SKU-DRAM-001", "name": "DRAM-16GB-DDR5", "cat": "Memory", "sup": "Samsung Electronics", "crit": "Critical", "unit_cost": 42.0},
        {"sku": "SKU-MCU-002", "name": "Automotive 32-Bit MCU", "cat": "Semiconductors", "sup": "TSMC Fab 14", "crit": "Critical", "unit_cost": 28.5},
        {"sku": "SKU-MOSFET-003", "name": "SiC 1200V MOSFET", "cat": "Power", "sup": "STMicroelectronics", "crit": "High", "unit_cost": 14.8},
        {"sku": "SKU-CAP-004", "name": "High-Temp MLCC 10uF", "cat": "Passives", "sup": "Murata Manufacturing", "crit": "Medium", "unit_cost": 1.25},
        {"sku": "SKU-IND-005", "name": "Shielded Power Inductor", "cat": "Passives", "sup": "TDK Electronics", "crit": "Medium", "unit_cost": 2.10},
        {"sku": "SKU-NAND-006", "name": "512GB UFS 4.0 Flash", "cat": "Memory", "sup": "SK Hynix", "crit": "High", "unit_cost": 34.0},
        {"sku": "SKU-PMIC-007", "name": "Multiphase PMIC 45A", "cat": "Power", "sup": "Texas Instruments", "crit": "High", "unit_cost": 8.70},
        {"sku": "SKU-HARNESS-008", "name": "HV Shielded Cable Harness", "cat": "Electromechanical", "sup": "Tata AutoComp Systems", "crit": "Medium", "unit_cost": 45.0},
        {"sku": "SKU-IGBT-009", "name": "750V 400A IGBT Module", "cat": "Power", "sup": "Infineon Technologies", "crit": "High", "unit_cost": 85.0},
        {"sku": "SKU-RADAR-010", "name": "77GHz mmWave Radar Sensor", "cat": "Sensors", "sup": "Bosch Mobility Electronics", "crit": "Critical", "unit_cost": 115.0},
        {"sku": "SKU-PCB-011", "name": "12-Layer HDI Substrate", "cat": "Substrates", "sup": "Foxconn Precision", "crit": "High", "unit_cost": 22.0},
        {"sku": "SKU-AUTO-012", "name": "R-Car V4H SoC", "cat": "Semiconductors", "sup": "Renesas Electronics", "crit": "Critical", "unit_cost": 92.0},
        {"sku": "SKU-LITH-013", "name": "Li-Ion 21700 Battery Cell", "cat": "Energy", "sup": "Samsung Electronics", "crit": "Critical", "unit_cost": 6.80},
        {"sku": "SKU-TIMING-014", "name": "Ultra-Low Jitter Oscillator", "cat": "Passives", "sup": "TDK Electronics", "crit": "Low", "unit_cost": 3.40},
        {"sku": "SKU-MEMS-015", "name": "6-Axis IMU Sensor", "cat": "Sensors", "sup": "STMicroelectronics", "crit": "Medium", "unit_cost": 4.60},
        {"sku": "SKU-ANALOG-016", "name": "Precision Op-Amp Dual", "cat": "Analog", "sup": "Texas Instruments", "crit": "Low", "unit_cost": 1.85},
        {"sku": "SKU-COOL-017", "name": "Vapor Chamber Heat Pipe", "cat": "Thermal", "sup": "Foxconn Precision", "crit": "Medium", "unit_cost": 7.20},
        {"sku": "SKU-CAN-018", "name": "Fault-Tolerant CAN Transceiver", "cat": "Semiconductors", "sup": "Bosch Mobility Electronics", "crit": "Medium", "unit_cost": 2.90},
        {"sku": "SKU-HBM-019", "name": "24GB HBM3 Memory Stack", "cat": "Memory", "sup": "SK Hynix", "crit": "Critical", "unit_cost": 320.0},
        {"sku": "SKU-GATE-020", "name": "Isolated SiC Gate Driver", "cat": "Power", "sup": "Infineon Technologies", "crit": "High", "unit_cost": 6.40},
    ]

    item_objs = {}
    for idx, sd in enumerate(skus_data):
        item = SupplyItem(
            business_id=business_id,
            name=sd["name"],
            category=sd["cat"],
            criticality=sd["crit"],
            primary_supplier_id=supplier_objs[sd["sup"]].id,
            alternate_supplier_count=1 if idx % 2 == 0 else 0,
            dependency_percentage=85.0 if idx == 1 else 60.0,
            monthly_consumption=f"{1200 + idx * 80} units",
            buffer_stock_days=15 if idx != 0 else 6,
            is_demo=True,
        )
        db.add(item)
        db.flush()
        item_objs[sd["sku"]] = item

        # Distribute inventory across warehouses
        for w_code, w_obj in warehouse_objs.items():
            # Setup specific situation for SKU-DRAM-001 at DC-SOUTH
            if sd["sku"] == "SKU-DRAM-001" and w_code == "DC-SOUTH":
                on_hand = 4280.0
                safety_stock = 5100.0
                status = "Critical"
                shortfall = 820.0
            elif sd["sku"] == "SKU-DRAM-001" and w_code == "DC-NORTH":
                on_hand = 9400.0
                safety_stock = 3500.0
                status = "Healthy"
                shortfall = 0.0
            elif sd["sku"] == "SKU-MCU-002" and w_code == "DC-SOUTH":
                on_hand = 1800.0
                safety_stock = 2500.0
                status = "Warning"
                shortfall = 700.0
            else:
                base_stock = 3000.0 + (idx * 200) % 4000
                on_hand = base_stock
                safety_stock = base_stock * 0.7
                status = "Healthy"
                shortfall = 0.0

            inv = InventoryRecord(
                business_id=business_id,
                warehouse_id=w_obj.id,
                supply_item_id=item.id,
                sku=sd["sku"],
                item_name=sd["name"],
                category=sd["cat"],
                on_hand=on_hand,
                allocated=on_hand * 0.25,
                on_order=1500.0,
                safety_stock=safety_stock,
                reorder_point=safety_stock * 1.3,
                unit_cost=sd["unit_cost"],
                lead_time_days=14,
                forecast_demand_30d=safety_stock * 0.95,
                shortfall=shortfall,
                status=status,
                is_demo=True,
            )
            db.add(inv)

    # 4. Supply Routes (15 intermodal routes connecting Suppliers, Ports, Warehouses, Factories)
    routes_data = [
        {"code": "RT-TW-US", "name": "Taiwan → Kaohsiung → Long Beach → DC South", "orig": "TSMC Fab 14", "dest": "DC South (Dallas)", "pts": ["Port of Kaohsiung", "Port of Long Beach"], "km": 11450.0, "days": 4.2, "cost": 62000.0, "co2": 8400.0, "mode": "Maritime", "status": "Disrupted", "risk": "High"},
        {"code": "RT-TW-US-ALT", "name": "Taiwan → Busan → Oakland → DC South [AI REROUTE]", "orig": "TSMC Fab 14", "dest": "DC South (Dallas)", "pts": ["Port of Busan", "Port of Oakland"], "km": 12280.0, "days": 4.8, "cost": 68500.0, "co2": 8920.0, "mode": "Maritime", "status": "Alternate", "risk": "Low"},
        {"code": "RT-KR-US", "name": "Hwaseong → Busan → Long Beach → DC South", "orig": "Samsung Electronics", "dest": "DC South (Dallas)", "pts": ["Port of Busan", "Port of Long Beach"], "km": 10900.0, "days": 3.9, "cost": 54000.0, "co2": 7800.0, "mode": "Maritime", "status": "Normal", "risk": "Low"},
        {"code": "RT-CN-EU", "name": "Shenzhen → Shanghai → Suez → Rotterdam → DC North", "orig": "Foxconn Precision", "dest": "DC North (Hamburg)", "pts": ["Port of Shanghai", "Suez Canal", "Port of Rotterdam"], "km": 19200.0, "days": 24.0, "cost": 78000.0, "co2": 14200.0, "mode": "Maritime", "status": "Congested", "risk": "High"},
        {"code": "RT-DE-US", "name": "Stuttgart → Frankfurt Air → Dallas Hub", "orig": "Bosch Mobility Electronics", "dest": "DC South (Dallas)", "pts": ["Frankfurt Cargo Hub", "DFW Airport"], "km": 8200.0, "days": 1.2, "cost": 38000.0, "co2": 19500.0, "mode": "Air", "status": "Normal", "risk": "Low"},
        {"code": "RT-JP-US", "name": "Tokyo → Yokohama → Long Beach → DC South", "orig": "Murata Manufacturing", "dest": "DC South (Dallas)", "pts": ["Port of Yokohama", "Port of Long Beach"], "km": 9800.0, "days": 3.6, "cost": 49000.0, "co2": 6900.0, "mode": "Maritime", "status": "Normal", "risk": "Low"},
        {"code": "RT-IN-EU", "name": "Pune → JNPT Mumbai → Suez → Rotterdam", "orig": "Tata AutoComp Systems", "dest": "DC North (Hamburg)", "pts": ["JNPT Mumbai", "Port of Rotterdam"], "km": 12800.0, "days": 18.0, "cost": 42000.0, "co2": 9200.0, "mode": "Maritime", "status": "Congested", "risk": "Medium"},
        {"code": "RT-FR-DE", "name": "Grenoble → Strasbourg → Hamburg DC North", "orig": "STMicroelectronics", "dest": "DC North (Hamburg)", "pts": ["Rhine Rail Corridor"], "km": 980.0, "days": 1.5, "cost": 7200.0, "co2": 450.0, "mode": "Rail", "status": "Normal", "risk": "Low"},
        {"code": "RT-DE-DE", "name": "Dresden → Berlin → Hamburg DC North", "orig": "Infineon Technologies", "dest": "DC North (Hamburg)", "pts": ["A24 Highway"], "km": 490.0, "days": 0.8, "cost": 3400.0, "co2": 380.0, "mode": "Road", "status": "Normal", "risk": "Low"},
        {"code": "RT-KR-JP", "name": "Icheon → Incheon Port → Tokyo Bay → DC West", "orig": "SK Hynix", "dest": "DC West (Tokyo)", "pts": ["Incheon Port", "Port of Tokyo"], "km": 1450.0, "days": 2.1, "cost": 11500.0, "co2": 1100.0, "mode": "Maritime", "status": "Normal", "risk": "Low"},
        {"code": "RT-US-DOM", "name": "Dallas Hub → Austin GigaFab Line Feed", "orig": "DC South (Dallas)", "dest": "Austin GigaFab", "pts": ["I-35 Freight Corridor"], "km": 315.0, "days": 0.4, "cost": 1850.0, "co2": 210.0, "mode": "Road", "status": "Normal", "risk": "Low"},
        {"code": "RT-DE-FAC", "name": "Hamburg Hub → Munich Assembly Plant", "orig": "DC North (Hamburg)", "dest": "Munich Assembly", "pts": ["A7 Express Route"], "km": 790.0, "days": 0.9, "cost": 4200.0, "co2": 520.0, "mode": "Road", "status": "Normal", "risk": "Low"},
        {"code": "RT-IN-DOM", "name": "Navi Mumbai Hub → Pune HighTech Plant", "orig": "DC Central (Mumbai)", "dest": "Pune HighTech Plant", "pts": ["Mumbai-Pune Expressway"], "km": 145.0, "days": 0.3, "cost": 920.0, "co2": 115.0, "mode": "Road", "status": "Normal", "risk": "Low"},
        {"code": "RT-INTER-DC", "name": "DC North (Hamburg) → DC South (Dallas) [REBALANCE]", "orig": "DC North (Hamburg)", "dest": "DC South (Dallas)", "pts": ["Rotterdam Port", "Port of Houston"], "km": 8700.0, "days": 6.5, "cost": 8420.0, "co2": 4800.0, "mode": "Maritime", "status": "Alternate", "risk": "Low"},
        {"code": "RT-US-WEST", "name": "Dallas Hub → Oakland Port → Customer West", "orig": "DC South (Dallas)", "dest": "Customer Regional Hub", "pts": ["I-40 Rail Hub"], "km": 2800.0, "days": 2.2, "cost": 12800.0, "co2": 1450.0, "mode": "Rail", "status": "Normal", "risk": "Low"},
    ]

    route_objs = {}
    for rd in routes_data:
        r = SupplyRoute(
            business_id=business_id,
            route_code=rd["code"],
            name=rd["name"],
            origin_type="Origin Hub",
            origin_name=rd["orig"],
            destination_type="Destination Node",
            destination_name=rd["dest"],
            waypoints=rd["pts"],
            distance_km=rd["km"],
            transit_time_days=rd["days"],
            cost_usd=rd["cost"],
            co2_kg=rd["co2"],
            primary_mode=rd["mode"],
            status=rd["status"],
            risk_level=rd["risk"],
            is_demo=True,
        )
        db.add(r)
        db.flush()
        route_objs[rd["code"]] = r

    # 5. Shipments (30 realistic active shipments)
    for i in range(1, 31):
        rt_code = routes_data[(i - 1) % len(routes_data)]["code"]
        rt = route_objs[rt_code]
        status = "Delayed" if rt.status == "Disrupted" else ("Rerouted" if rt.status == "Alternate" else "In Transit")
        delay_hrs = 14.4 if status == "Delayed" else (0.0 if status == "In Transit" else 4.0)

        shipment = SupplyShipment(
            business_id=business_id,
            route_id=rt.id,
            tracking_number=f"TRK-PH-2026-{1000 + i}",
            cargo_description=f"Consolidated Freight: {skus_data[i % len(skus_data)]['name']} (Pallet #{i})",
            cargo_value_usd=round(45000.0 + (i * 3500.0), 2),
            origin=rt.origin_name,
            destination=rt.destination_name,
            current_location=rt.waypoints[0] if rt.waypoints else rt.origin_name,
            eta_days=round(rt.transit_time_days + (delay_hrs / 24.0), 1),
            delay_hours=delay_hrs,
            status=status,
            is_demo=True,
        )
        db.add(shipment)

    # 6. Active Disruptions (3 live-looking enterprise disruptions)
    disruptions_data = [
        {
            "signal_id": "SIG-TYPHOON-GAEMI",
            "title": "Port of Kaohsiung Severe Congestion & Berth Closure",
            "type": "cyclone",
            "severity": "High",
            "conf": 0.94,
            "region": "Taiwan Strait",
            "nodes": ["TSMC Fab 14", "Port of Kaohsiung", "RT-TW-US"],
            "delay": 8.0,
            "impact_usd": 420000.0,
            "phase": "active",
            "desc": "Category 4 Typhoon Gaemi causing high swell and berth shutdowns at Port of Kaohsiung. 4 maritime container vessels delayed with estimated 8-day port turnaround backlog.",
            "commodities": {"semiconductors": 1.15, "shipping_container_40ft": 1.25},
        },
        {
            "signal_id": "SIG-RED-SEA-BOTTLENECK",
            "title": "Suez / Red Sea Maritime Bottleneck & Security Re-routing",
            "type": "geopolitical",
            "severity": "High",
            "conf": 0.88,
            "region": "Bab el-Mandeb / Red Sea",
            "nodes": ["RT-CN-EU", "RT-IN-EU", "Port of Rotterdam"],
            "delay": 12.0,
            "impact_usd": 680000.0,
            "phase": "active",
            "desc": "Commercial freight vessels rerouting around Cape of Good Hope due to regional maritime security alerts. Extending EU delivery lead times by 10-14 days.",
            "commodities": {"crude_oil": 1.08, "shipping_container_40ft": 1.40},
        },
        {
            "signal_id": "SIG-DRAM-STOCKOUT-DALLAS",
            "title": "DRAM Buffer Critical Depletion at DC South",
            "type": "supplier_outage",
            "severity": "Medium",
            "conf": 0.92,
            "region": "North America Logistics Corridor",
            "nodes": ["DC South (Dallas)", "SKU-DRAM-001", "Austin GigaFab"],
            "delay": 6.0,
            "impact_usd": 210000.0,
            "phase": "warning",
            "desc": "DC South inventory position for DRAM-16GB-DDR5 is 4,280 units against safety stock of 5,100 (-820 shortfall). Buffer depletion expected within 6 operating days without rebalancing.",
            "commodities": {"semiconductors": 1.06},
        },
    ]

    disruption_objs = {}
    for dd in disruptions_data:
        de = DisruptionEvent(
            business_id=business_id,
            signal_id=dd["signal_id"],
            title=dd["title"],
            disruption_type=dd["type"],
            severity=dd["severity"],
            confidence=dd["conf"],
            affected_region=dd["region"],
            affected_node_ids=dd["nodes"],
            impact_delay_days=dd["delay"],
            financial_impact_usd=dd["impact_usd"],
            lifecycle_phase=dd["phase"],
            description=dd["desc"],
            commodity_effects=dd["commodities"],
            status="Active",
            is_demo=True,
        )
        db.add(de)
        db.flush()
        disruption_objs[dd["signal_id"]] = de

    # 7. AI Recommendations Awaiting Human Approval
    rec1 = AIRecommendation(
        business_id=business_id,
        disruption_id=disruption_objs["SIG-TYPHOON-GAEMI"].id,
        title="Activate OR-Tools Bypass: Kaohsiung → Busan → Oakland Reroute",
        recommendation_type="reroute_shipment",
        description="Divert 4 container shipments via Port of Busan feeder vessels and Port of Oakland railhead to circumvent 8-day Kaohsiung port congestion.",
        expected_cost_usd=6500.0,
        expected_delay_reduction_days=7.4,
        expected_risk_reduction_pct=64.0,
        requires_human_approval=True,
        approval_status="PENDING",
        explanation_why=(
            "1. Port of Kaohsiung is experiencing active typhoon closure with a 3-5 day vessel queue.\n"
            "2. OR-Tools calculated minimum-cost bypass via Busan Port (+14.4 hours transit delta).\n"
            "3. Prevents an estimated $420,000 downstream Austin assembly line stoppage at a cost of only $6,500 (+10.5%)."
        ),
        action_payload={
            "action": "reroute_shipment",
            "target_routes": ["RT-TW-US"],
            "alternative_route": "RT-TW-US-ALT",
            "affected_shipments": ["TRK-PH-2026-1001", "TRK-PH-2026-1016"],
        },
        is_demo=True,
    )
    db.add(rec1)

    rec2 = AIRecommendation(
        business_id=business_id,
        disruption_id=disruption_objs["SIG-DRAM-STOCKOUT-DALLAS"].id,
        title="Rebalance 800 Units of DRAM from DC North to DC South",
        recommendation_type="rebalance_inventory",
        description="Transfer 800 units of SKU-DRAM-001 from surplus inventory at DC North (Hamburg) to eliminate stockout risk at DC South (Dallas).",
        expected_cost_usd=8420.0,
        expected_delay_reduction_days=6.0,
        expected_risk_reduction_pct=72.0,
        requires_human_approval=True,
        approval_status="PENDING",
        explanation_why=(
            "1. DC South is projected to fall below safety buffer in 6 days with an 820-unit shortfall.\n"
            "2. DC North has 9,400 units on hand (2.4× safety stock requirement), providing safe surplus buffer.\n"
            "3. Inter-DC transfer reduces stockout probability by 72% for $8,420 in freight costs."
        ),
        action_payload={
            "action": "rebalance_inventory",
            "sku": "SKU-DRAM-001",
            "source_warehouse": "DC North (Hamburg)",
            "target_warehouse": "DC South (Dallas)",
            "quantity": 800,
        },
        is_demo=True,
    )
    db.add(rec2)

    rec3 = AIRecommendation(
        business_id=business_id,
        disruption_id=disruption_objs["SIG-TYPHOON-GAEMI"].id,
        title="Qualify Secondary Allocation: Samsung Electronics Hwaseong",
        recommendation_type="switch_supplier",
        description="Shift 35% of microcontroller buffer order volume from TSMC Fab 14 to pre-audited secondary supplier Samsung Electronics.",
        expected_cost_usd=14200.0,
        expected_delay_reduction_days=4.0,
        expected_risk_reduction_pct=31.0,
        requires_human_approval=True,
        approval_status="APPROVED",
        approved_by="VP Supply Chain Operations",
        approved_at=datetime.utcnow() - timedelta(hours=4),
        explanation_why=(
            "1. Sole-source dependency on TSMC Fab 14 stands at 85% with high geopolitical corridor concentration.\n"
            "2. Samsung Electronics Hwaseong holds valid ISO 9001 and automotive AEC-Q100 certifications.\n"
            "3. Multi-sourcing reduces vendor risk index by 31% with a minor +8.2% procurement delta."
        ),
        action_payload={
            "action": "switch_supplier",
            "primary_supplier": "TSMC Fab 14",
            "backup_supplier": "Samsung Electronics",
            "volume_percentage": 35.0,
        },
        is_demo=True,
    )
    db.add(rec3)

    # 8. Pre-simulated Scenarios
    scenarios_seed = [
        {"name": "Scenario A — Port of Kaohsiung Closure (10 Days)", "type": "port_closure", "params": {"port": "Port of Kaohsiung", "delay_days": 10, "affected_suppliers": 3, "affected_skus": 8}, "cost": 18.5, "delay": 10.0, "risk": 74.0, "rec_days": 16.0, "ai_cost": 8.5, "ai_delay": 3.8, "ai_risk": 29.0, "ai_rec_days": 5.0},
        {"name": "Scenario B — Primary Supplier Failure (TSMC 30 Days)", "type": "supplier_failure", "params": {"supplier": "TSMC Fab 14", "duration_days": 30, "backup_ratio": 0.40}, "cost": 26.0, "delay": 18.0, "risk": 86.0, "rec_days": 34.0, "ai_cost": 12.0, "ai_delay": 6.5, "ai_risk": 38.0, "ai_rec_days": 11.0},
        {"name": "Scenario C — East Asia Tariff Increase (+20%)", "type": "tariff_increase", "params": {"tariff_pct": 20.0, "corridor": "Transpacific Eastbound"}, "cost": 20.0, "delay": 2.0, "risk": 58.0, "rec_days": 12.0, "ai_cost": 6.0, "ai_delay": 1.0, "ai_risk": 24.0, "ai_rec_days": 4.0},
        {"name": "Scenario D — Severe Winter Logistics Freeze (North America)", "type": "severe_weather", "params": {"region": "US Central Corridor", "delay_days": 7}, "cost": 15.0, "delay": 8.0, "risk": 68.0, "rec_days": 14.0, "ai_cost": 7.0, "ai_delay": 2.5, "ai_risk": 28.0, "ai_rec_days": 4.5},
    ]

    for sc in scenarios_seed:
        scenario = SupplyScenario(
            business_id=business_id,
            name=sc["name"],
            scenario_type=sc["type"],
            parameters=sc["params"],
            status="Simulated",
            is_demo=True,
        )
        db.add(scenario)
        db.flush()

        res = SupplyScenarioResult(
            scenario_id=scenario.id,
            business_id=business_id,
            cost_impact_pct=sc["cost"],
            delay_impact_days=sc["delay"],
            scenario_risk_score=sc["risk"],
            scenario_recovery_days=sc["rec_days"],
            ai_cost_impact_pct=sc["ai_cost"],
            ai_delay_days=sc["ai_delay"],
            ai_risk_score=sc["ai_risk"],
            ai_recovery_days=sc["ai_rec_days"],
            comparison_data={
                "metrics": [
                    {"dimension": "Cost Impact", "baseline": 0, "disrupted": sc["cost"], "ai_recovered": sc["ai_cost"], "unit": "%"},
                    {"dimension": "Transit Delay", "baseline": 0, "disrupted": sc["delay"], "ai_recovered": sc["ai_delay"], "unit": "days"},
                    {"dimension": "Risk Score", "baseline": 18, "disrupted": sc["risk"], "ai_recovered": sc["ai_risk"], "unit": "pts"},
                    {"dimension": "Recovery Time", "baseline": 0, "disrupted": sc["rec_days"], "ai_recovered": sc["ai_rec_days"], "unit": "days"},
                ]
            },
            ai_summary=(
                f"Under {sc['name']}, unmitigated disruption increases freight costs by +{sc['cost']}% "
                f"with a {sc['delay']}-day shipping delay. The Supply Chain AI stack (SupplyMind + Inventory Fusion + OR-Tools) "
                f"restricts cost rise to +{sc['ai_cost']}% and compresses recovery to {sc['ai_rec_days']} days."
            ),
        )
        db.add(res)

    # 9. Supply Chain Audit Trail Records
    now = datetime.utcnow()
    audits = [
        {"ts": now - timedelta(minutes=45), "agent": "Disruption Agent (SupplyMind)", "action": "Detected Category 4 Typhoon Gaemi swell at Port of Kaohsiung", "reason": "AIS vessel transponder speed drops and marine advisory notice", "risk": "Critical", "appr": False, "dec": "DISRUPTION_TRIGGERED"},
        {"ts": now - timedelta(minutes=42), "agent": "Scenario Agent (SupplyMind + Qwen3)", "action": "Simulated 4 recovery options across transpacific corridors", "reason": "Evaluated Cape route vs Busan bypass vs Air freight buffer", "risk": "High", "appr": False, "dec": "OPTIMAL_BYPASS_FOUND"},
        {"ts": now - timedelta(minutes=38), "agent": "Logistics Agent (Google OR-Tools)", "action": "Generated optimal bypass via Busan and Port of Oakland", "reason": "OR-Tools capacity & transit optimization (+14.4h, +$6,500)", "risk": "Medium", "appr": True, "dec": "AWAITING_APPROVAL"},
        {"ts": now - timedelta(minutes=32), "agent": "Inventory Agent (Inventory Fusion)", "action": "Identified critical buffer shortfall at DC South for DRAM-16GB-DDR5", "reason": "Net position (4,280) vs Safety stock (5,100) indicates 6-day stockout", "risk": "High", "appr": False, "dec": "REBALANCE_TRIGGERED"},
        {"ts": now - timedelta(minutes=28), "agent": "Inventory Rebalancing Agent", "action": "Recommended 800-unit inter-DC stock transfer (DC North -> DC South)", "reason": "Surplus buffer available at DC North; 72% shortage reduction achieved", "risk": "Low", "appr": True, "dec": "AWAITING_APPROVAL"},
        {"ts": now - timedelta(minutes=15), "agent": "Supplier Risk Engine (DistilBERT + HREDD)", "action": "Assessed TSMC Fab 14 and qualified Samsung Electronics for secondary volume", "reason": "Sole-source mitigation reduces dependency concentration by 31%", "risk": "Medium", "appr": True, "dec": "RECOMMENDED"},
        {"ts": now - timedelta(minutes=10), "agent": "Human Approval Gate", "action": "VP Supply Chain approved Samsung Electronics secondary volume allocation", "reason": "Authorised under Emergency Sourcing Delegation Policy §4.2", "risk": "Low", "appr": True, "dec": "APPROVED"},
    ]

    for a in audits:
        audit_rec = SupplyChainAudit(
            business_id=business_id,
            timestamp=a["ts"],
            agent_name=a["agent"],
            action=a["action"],
            reason=a["reason"],
            risk_level=a["risk"],
            approval_required=a["appr"],
            decision=a["dec"],
            data_used={"engine": a["agent"], "verified": True},
            is_demo=True,
        )
        db.add(audit_rec)

    db.commit()

    return {
        "status": "success",
        "warehouses": len(warehouse_objs),
        "suppliers": len(supplier_objs),
        "skus": len(item_objs),
        "routes": len(route_objs),
        "shipments": 30,
        "disruptions": len(disruption_objs),
        "recommendations": 3,
        "scenarios": len(scenarios_seed),
        "audits": len(audits),
    }


def cleanup_control_tower_demo_data(db: Session, business_id: str) -> None:
    """Safely remove all demo records for the supply chain control tower."""
    db.query(SupplyChainAudit).filter(SupplyChainAudit.business_id == business_id, SupplyChainAudit.is_demo == True).delete()
    db.query(AIRecommendation).filter(AIRecommendation.business_id == business_id, AIRecommendation.is_demo == True).delete()
    db.query(SupplyScenarioResult).filter(SupplyScenarioResult.business_id == business_id).delete()
    db.query(SupplyScenario).filter(SupplyScenario.business_id == business_id, SupplyScenario.is_demo == True).delete()
    db.query(DisruptionEvent).filter(DisruptionEvent.business_id == business_id, DisruptionEvent.is_demo == True).delete()
    db.query(SupplyShipment).filter(SupplyShipment.business_id == business_id, SupplyShipment.is_demo == True).delete()
    db.query(SupplyRoute).filter(SupplyRoute.business_id == business_id, SupplyRoute.is_demo == True).delete()
    db.query(InventoryRecord).filter(InventoryRecord.business_id == business_id, InventoryRecord.is_demo == True).delete()
    db.query(Warehouse).filter(Warehouse.business_id == business_id, Warehouse.is_demo == True).delete()
    db.commit()
