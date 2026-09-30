"""add_supply_chain_control_tower_models

Revision ID: f603c9d0a1b5
Revises: e592b8c9f3a4
Create Date: 2026-09-30 05:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f603c9d0a1b5'
down_revision: Union[str, None] = 'e592b8c9f3a4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. supply_warehouses
    op.create_table(
        'supply_warehouses',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('business_id', sa.String(length=36), sa.ForeignKey('business_profiles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('warehouse_type', sa.String(length=100), nullable=False, server_default='Distribution Center'),
        sa.Column('location', sa.String(length=100), nullable=False),
        sa.Column('country', sa.String(length=100), nullable=False, server_default='United States'),
        sa.Column('lat', sa.Float(), nullable=True),
        sa.Column('lng', sa.Float(), nullable=True),
        sa.Column('capacity_units', sa.Integer(), nullable=False, server_default='50000'),
        sa.Column('utilized_units', sa.Integer(), nullable=False, server_default='32000'),
        sa.Column('operating_cost_per_day', sa.Float(), nullable=False, server_default='1250.0'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='Operational'),
        sa.Column('is_demo', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_supply_warehouses_business_id', 'supply_warehouses', ['business_id'])
    op.create_index('ix_supply_warehouses_code', 'supply_warehouses', ['code'])

    # 2. supply_inventory_records
    op.create_table(
        'supply_inventory_records',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('business_id', sa.String(length=36), sa.ForeignKey('business_profiles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('warehouse_id', sa.String(length=36), sa.ForeignKey('supply_warehouses.id', ondelete='CASCADE'), nullable=False),
        sa.Column('supply_item_id', sa.String(length=36), sa.ForeignKey('supply_items.id', ondelete='SET NULL'), nullable=True),
        sa.Column('sku', sa.String(length=100), nullable=False),
        sa.Column('item_name', sa.String(length=255), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=False, server_default='Semiconductors'),
        sa.Column('on_hand', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('allocated', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('on_order', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('safety_stock', sa.Float(), nullable=False, server_default='1000.0'),
        sa.Column('reorder_point', sa.Float(), nullable=False, server_default='1500.0'),
        sa.Column('unit_cost', sa.Float(), nullable=False, server_default='10.0'),
        sa.Column('holding_cost_rate', sa.Float(), nullable=False, server_default='0.18'),
        sa.Column('lead_time_days', sa.Integer(), nullable=False, server_default='14'),
        sa.Column('forecast_demand_30d', sa.Float(), nullable=False, server_default='1200.0'),
        sa.Column('shortfall', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='Healthy'),
        sa.Column('is_demo', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_supply_inventory_records_business_id', 'supply_inventory_records', ['business_id'])
    op.create_index('ix_supply_inventory_records_warehouse_id', 'supply_inventory_records', ['warehouse_id'])
    op.create_index('ix_supply_inventory_records_sku', 'supply_inventory_records', ['sku'])

    # 3. supply_routes
    op.create_table(
        'supply_routes',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('business_id', sa.String(length=36), sa.ForeignKey('business_profiles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('route_code', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('origin_type', sa.String(length=50), nullable=False),
        sa.Column('origin_name', sa.String(length=100), nullable=False),
        sa.Column('destination_type', sa.String(length=50), nullable=False),
        sa.Column('destination_name', sa.String(length=100), nullable=False),
        sa.Column('waypoints', sa.JSON(), nullable=False),
        sa.Column('distance_km', sa.Float(), nullable=False, server_default='1200.0'),
        sa.Column('transit_time_days', sa.Float(), nullable=False, server_default='4.5'),
        sa.Column('cost_usd', sa.Float(), nullable=False, server_default='4500.0'),
        sa.Column('co2_kg', sa.Float(), nullable=False, server_default='850.0'),
        sa.Column('primary_mode', sa.String(length=50), nullable=False, server_default='Maritime'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='Normal'),
        sa.Column('risk_level', sa.String(length=50), nullable=False, server_default='Low'),
        sa.Column('is_demo', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_supply_routes_business_id', 'supply_routes', ['business_id'])
    op.create_index('ix_supply_routes_route_code', 'supply_routes', ['route_code'])

    # 4. supply_shipments
    op.create_table(
        'supply_shipments',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('business_id', sa.String(length=36), sa.ForeignKey('business_profiles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('route_id', sa.String(length=36), sa.ForeignKey('supply_routes.id', ondelete='SET NULL'), nullable=True),
        sa.Column('tracking_number', sa.String(length=100), nullable=False),
        sa.Column('cargo_description', sa.String(length=255), nullable=False),
        sa.Column('cargo_value_usd', sa.Float(), nullable=False, server_default='50000.0'),
        sa.Column('origin', sa.String(length=100), nullable=False),
        sa.Column('destination', sa.String(length=100), nullable=False),
        sa.Column('current_location', sa.String(length=100), nullable=False),
        sa.Column('eta_days', sa.Float(), nullable=False, server_default='3.0'),
        sa.Column('delay_hours', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='In Transit'),
        sa.Column('is_demo', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_supply_shipments_business_id', 'supply_shipments', ['business_id'])
    op.create_index('ix_supply_shipments_tracking_number', 'supply_shipments', ['tracking_number'])

    # 5. supply_disruptions
    op.create_table(
        'supply_disruptions',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('business_id', sa.String(length=36), sa.ForeignKey('business_profiles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('signal_id', sa.String(length=100), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('disruption_type', sa.String(length=100), nullable=False),
        sa.Column('severity', sa.String(length=50), nullable=False, server_default='High'),
        sa.Column('confidence', sa.Float(), nullable=False, server_default='0.85'),
        sa.Column('affected_region', sa.String(length=100), nullable=False),
        sa.Column('affected_node_ids', sa.JSON(), nullable=False),
        sa.Column('impact_delay_days', sa.Float(), nullable=False, server_default='7.0'),
        sa.Column('financial_impact_usd', sa.Float(), nullable=False, server_default='250000.0'),
        sa.Column('lifecycle_phase', sa.String(length=50), nullable=False, server_default='active'),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('commodity_effects', sa.JSON(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='Active'),
        sa.Column('detected_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('is_demo', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_supply_disruptions_business_id', 'supply_disruptions', ['business_id'])
    op.create_index('ix_supply_disruptions_signal_id', 'supply_disruptions', ['signal_id'])

    # 6. supply_scenarios
    op.create_table(
        'supply_scenarios',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('business_id', sa.String(length=36), sa.ForeignKey('business_profiles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('scenario_type', sa.String(length=100), nullable=False),
        sa.Column('parameters', sa.JSON(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='Simulated'),
        sa.Column('is_demo', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_supply_scenarios_business_id', 'supply_scenarios', ['business_id'])

    # 7. supply_scenario_results
    op.create_table(
        'supply_scenario_results',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('scenario_id', sa.String(length=36), sa.ForeignKey('supply_scenarios.id', ondelete='CASCADE'), nullable=False),
        sa.Column('business_id', sa.String(length=36), sa.ForeignKey('business_profiles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('cost_impact_pct', sa.Float(), nullable=False, server_default='18.0'),
        sa.Column('delay_impact_days', sa.Float(), nullable=False, server_default='11.0'),
        sa.Column('scenario_risk_score', sa.Float(), nullable=False, server_default='72.0'),
        sa.Column('scenario_recovery_days', sa.Float(), nullable=False, server_default='16.0'),
        sa.Column('ai_cost_impact_pct', sa.Float(), nullable=False, server_default='8.0'),
        sa.Column('ai_delay_days', sa.Float(), nullable=False, server_default='4.0'),
        sa.Column('ai_risk_score', sa.Float(), nullable=False, server_default='31.0'),
        sa.Column('ai_recovery_days', sa.Float(), nullable=False, server_default='6.0'),
        sa.Column('comparison_data', sa.JSON(), nullable=False),
        sa.Column('ai_summary', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_supply_scenario_results_business_id', 'supply_scenario_results', ['business_id'])
    op.create_index('ix_supply_scenario_results_scenario_id', 'supply_scenario_results', ['scenario_id'])

    # 8. supply_ai_recommendations
    op.create_table(
        'supply_ai_recommendations',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('business_id', sa.String(length=36), sa.ForeignKey('business_profiles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('disruption_id', sa.String(length=36), sa.ForeignKey('supply_disruptions.id', ondelete='SET NULL'), nullable=True),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('recommendation_type', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('expected_cost_usd', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('expected_delay_reduction_days', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('expected_risk_reduction_pct', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('requires_human_approval', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('approval_status', sa.String(length=50), nullable=False, server_default='PENDING'),
        sa.Column('approved_by', sa.String(length=100), nullable=True),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.Column('rejection_reason', sa.Text(), nullable=True),
        sa.Column('explanation_why', sa.Text(), nullable=False),
        sa.Column('action_payload', sa.JSON(), nullable=False),
        sa.Column('is_demo', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_supply_ai_recommendations_business_id', 'supply_ai_recommendations', ['business_id'])

    # 9. supply_chain_audits
    op.create_table(
        'supply_chain_audits',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('business_id', sa.String(length=36), sa.ForeignKey('business_profiles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('agent_name', sa.String(length=100), nullable=False),
        sa.Column('action', sa.String(length=255), nullable=False),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.Column('data_used', sa.JSON(), nullable=False),
        sa.Column('risk_level', sa.String(length=50), nullable=False, server_default='Medium'),
        sa.Column('approval_required', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('decision', sa.String(length=100), nullable=False, server_default='RECOMMENDED'),
        sa.Column('is_demo', sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.create_index('ix_supply_chain_audits_business_id', 'supply_chain_audits', ['business_id'])
    op.create_index('ix_supply_chain_audits_timestamp', 'supply_chain_audits', ['timestamp'])


def downgrade() -> None:
    op.drop_table('supply_chain_audits')
    op.drop_table('supply_ai_recommendations')
    op.drop_table('supply_scenario_results')
    op.drop_table('supply_scenarios')
    op.drop_table('supply_disruptions')
    op.drop_table('supply_shipments')
    op.drop_table('supply_routes')
    op.drop_table('supply_inventory_records')
    op.drop_table('supply_warehouses')
