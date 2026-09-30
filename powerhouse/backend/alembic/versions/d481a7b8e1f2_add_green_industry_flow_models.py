"""add_green_industry_flow_models

Revision ID: d481a7b8e1f2
Revises: c912a7f8e3b1
Create Date: 2026-09-15 21:58:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd481a7b8e1f2'
down_revision: Union[str, None] = 'c912a7f8e3b1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. green_opportunities
    op.create_table(
        'green_opportunities',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('business_profile_id', sa.String(length=36), sa.ForeignKey('business_profiles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('agent_type', sa.String(length=100), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=False),
        sa.Column('priority', sa.String(length=50), nullable=False, server_default='Medium'),
        sa.Column('severity', sa.String(length=50), nullable=False, server_default='Warning'),
        sa.Column('detected_issue', sa.Text(), nullable=False),
        sa.Column('evidence', sa.JSON(), nullable=False),
        sa.Column('cause', sa.Text(), nullable=False),
        sa.Column('recommended_action', sa.Text(), nullable=False),
        sa.Column('estimated_cost_impact', sa.JSON(), nullable=True),
        sa.Column('estimated_energy_impact', sa.JSON(), nullable=True),
        sa.Column('estimated_carbon_impact', sa.JSON(), nullable=True),
        sa.Column('implementation_effort', sa.String(length=50), nullable=False, server_default='Medium'),
        sa.Column('confidence', sa.Float(), nullable=False, server_default='0.85'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='DETECTED'),
        sa.Column('policy_status', sa.String(length=50), nullable=False, server_default='PASS'),
        sa.Column('policy_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('reviewed_at', sa.DateTime(), nullable=True),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
    )
    op.create_index(op.f('ix_green_opportunities_id'), 'green_opportunities', ['id'], unique=False)
    op.create_index(op.f('ix_green_opportunities_business_profile_id'), 'green_opportunities', ['business_profile_id'], unique=False)
    op.create_index(op.f('ix_green_opportunities_status'), 'green_opportunities', ['status'], unique=False)

    # 2. emission_factors
    op.create_table(
        'emission_factors',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('name', sa.String(length=255), nullable=False, unique=True),
        sa.Column('value', sa.Float(), nullable=False),
        sa.Column('unit', sa.String(length=50), nullable=False),
        sa.Column('source', sa.String(length=255), nullable=False),
        sa.Column('source_version', sa.String(length=50), nullable=True),
        sa.Column('geography', sa.String(length=100), nullable=False, server_default='India - National Grid'),
        sa.Column('scope', sa.String(length=50), nullable=False, server_default='Scope 2'),
        sa.Column('effective_date', sa.String(length=50), nullable=True),
        sa.Column('review_date', sa.String(length=50), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='VERIFIED'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index(op.f('ix_emission_factors_id'), 'emission_factors', ['id'], unique=False)

    # 3. green_impact_measurements
    op.create_table(
        'green_impact_measurements',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('opportunity_id', sa.String(length=36), sa.ForeignKey('green_opportunities.id', ondelete='CASCADE'), nullable=False),
        sa.Column('business_profile_id', sa.String(length=36), sa.ForeignKey('business_profiles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('metric_name', sa.String(length=100), nullable=False),
        sa.Column('unit', sa.String(length=50), nullable=False),
        sa.Column('baseline_value', sa.Float(), nullable=False),
        sa.Column('measured_value', sa.Float(), nullable=True),
        sa.Column('absolute_change', sa.Float(), nullable=True),
        sa.Column('percentage_change', sa.Float(), nullable=True),
        sa.Column('is_demo', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('verification_status', sa.String(length=50), nullable=False, server_default='PENDING'),
        sa.Column('formula', sa.String(length=255), nullable=False),
        sa.Column('assumptions', sa.Text(), nullable=True),
        sa.Column('verified_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_index(op.f('ix_green_impact_measurements_id'), 'green_impact_measurements', ['id'], unique=False)
    op.create_index(op.f('ix_green_impact_measurements_opportunity_id'), 'green_impact_measurements', ['opportunity_id'], unique=False)
    op.create_index(op.f('ix_green_impact_measurements_business_profile_id'), 'green_impact_measurements', ['business_profile_id'], unique=False)

    # 4. agent_runs
    op.create_table(
        'agent_runs',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('business_profile_id', sa.String(length=36), sa.ForeignKey('business_profiles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('agent_type', sa.String(length=100), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='RUNNING'),
        sa.Column('input_sources', sa.JSON(), nullable=False),
        sa.Column('output_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('trace_steps', sa.JSON(), nullable=False),
        sa.Column('error', sa.Text(), nullable=True),
        sa.Column('model_used', sa.String(length=100), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
    )
    op.create_index(op.f('ix_agent_runs_id'), 'agent_runs', ['id'], unique=False)
    op.create_index(op.f('ix_agent_runs_business_profile_id'), 'agent_runs', ['business_profile_id'], unique=False)

    # 5. green_operational_metrics
    op.create_table(
        'green_operational_metrics',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('business_profile_id', sa.String(length=36), sa.ForeignKey('business_profiles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('metric_type', sa.String(length=100), nullable=False),
        sa.Column('value', sa.Float(), nullable=False),
        sa.Column('unit', sa.String(length=50), nullable=False),
        sa.Column('is_demo', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('label', sa.String(length=255), nullable=True),
        sa.Column('collected_at', sa.DateTime(), nullable=False),
    )
    op.create_index(op.f('ix_green_operational_metrics_id'), 'green_operational_metrics', ['id'], unique=False)
    op.create_index(op.f('ix_green_operational_metrics_business_profile_id'), 'green_operational_metrics', ['business_profile_id'], unique=False)
    op.create_index(op.f('ix_green_operational_metrics_metric_type'), 'green_operational_metrics', ['metric_type'], unique=False)


def downgrade() -> None:
    op.drop_table('green_operational_metrics')
    op.drop_table('agent_runs')
    op.drop_table('green_impact_measurements')
    op.drop_table('emission_factors')
    op.drop_table('green_opportunities')
