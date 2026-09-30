"""add_supply_chain_and_workforce_models

Revision ID: e592b8c9f3a4
Revises: d481a7b8e1f2
Create Date: 2026-09-18 22:15:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e592b8c9f3a4'
down_revision: Union[str, None] = 'd481a7b8e1f2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. suppliers
    op.create_table(
        'suppliers',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('business_id', sa.String(length=36), sa.ForeignKey('business_profiles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('supplier_type', sa.String(length=100), nullable=False, server_default='Raw Material'),
        sa.Column('location', sa.String(length=100), nullable=False),
        sa.Column('country', sa.String(length=100), nullable=False, server_default='India'),
        sa.Column('products_or_materials', sa.JSON(), nullable=False),
        sa.Column('dependency_percentage', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('lead_time_days', sa.Integer(), nullable=False, server_default='7'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='Active'),
        sa.Column('contact_information', sa.JSON(), nullable=True),
        sa.Column('risk_status', sa.String(length=50), nullable=False, server_default='Low'),
        sa.Column('is_demo', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index(op.f('ix_suppliers_id'), 'suppliers', ['id'], unique=False)
    op.create_index(op.f('ix_suppliers_business_id'), 'suppliers', ['business_id'], unique=False)
    op.create_index(op.f('ix_suppliers_name'), 'suppliers', ['name'], unique=False)

    # 2. supplier_documents
    op.create_table(
        'supplier_documents',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('supplier_id', sa.String(length=36), sa.ForeignKey('suppliers.id', ondelete='CASCADE'), nullable=False),
        sa.Column('document_id', sa.String(length=36), sa.ForeignKey('documents.id', ondelete='SET NULL'), nullable=True),
        sa.Column('document_name', sa.String(length=255), nullable=False),
        sa.Column('document_type', sa.String(length=100), nullable=False),
        sa.Column('verification_status', sa.String(length=50), nullable=False, server_default='Pending'),
        sa.Column('expiry_date', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index(op.f('ix_supplier_documents_id'), 'supplier_documents', ['id'], unique=False)
    op.create_index(op.f('ix_supplier_documents_supplier_id'), 'supplier_documents', ['supplier_id'], unique=False)

    # 3. supply_items
    op.create_table(
        'supply_items',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('business_id', sa.String(length=36), sa.ForeignKey('business_profiles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=False, server_default='Raw Material'),
        sa.Column('criticality', sa.String(length=50), nullable=False, server_default='High'),
        sa.Column('primary_supplier_id', sa.String(length=36), sa.ForeignKey('suppliers.id', ondelete='SET NULL'), nullable=True),
        sa.Column('alternate_supplier_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('dependency_percentage', sa.Float(), nullable=False, server_default='100.0'),
        sa.Column('monthly_consumption', sa.String(length=100), nullable=True),
        sa.Column('buffer_stock_days', sa.Integer(), nullable=False, server_default='15'),
        sa.Column('is_demo', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index(op.f('ix_supply_items_id'), 'supply_items', ['id'], unique=False)
    op.create_index(op.f('ix_supply_items_business_id'), 'supply_items', ['business_id'], unique=False)
    op.create_index(op.f('ix_supply_items_name'), 'supply_items', ['name'], unique=False)

    # 4. supply_chain_risks
    op.create_table(
        'supply_chain_risks',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('business_id', sa.String(length=36), sa.ForeignKey('business_profiles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('supplier_id', sa.String(length=36), sa.ForeignKey('suppliers.id', ondelete='SET NULL'), nullable=True),
        sa.Column('supply_item_id', sa.String(length=36), sa.ForeignKey('supply_items.id', ondelete='SET NULL'), nullable=True),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=False),
        sa.Column('priority', sa.String(length=50), nullable=False, server_default='High'),
        sa.Column('severity', sa.String(length=50), nullable=False, server_default='Warning'),
        sa.Column('evidence', sa.JSON(), nullable=False),
        sa.Column('issue', sa.Text(), nullable=False),
        sa.Column('cause', sa.Text(), nullable=False),
        sa.Column('recommended_action', sa.Text(), nullable=False),
        sa.Column('estimated_cost', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('estimated_risk_reduction', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('effort', sa.String(length=50), nullable=False, server_default='Medium'),
        sa.Column('confidence', sa.Float(), nullable=False, server_default='0.85'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='DETECTED'),
        sa.Column('policy_check_status', sa.String(length=50), nullable=False, server_default='PASS'),
        sa.Column('is_demo', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('detected_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index(op.f('ix_supply_chain_risks_id'), 'supply_chain_risks', ['id'], unique=False)
    op.create_index(op.f('ix_supply_chain_risks_business_id'), 'supply_chain_risks', ['business_id'], unique=False)

    # 5. employee_profiles
    op.create_table(
        'employee_profiles',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('business_id', sa.String(length=36), sa.ForeignKey('business_profiles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('employee_reference', sa.String(length=100), nullable=False),
        sa.Column('role', sa.String(length=100), nullable=False),
        sa.Column('department', sa.String(length=100), nullable=False),
        sa.Column('experience_years', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('current_skills', sa.JSON(), nullable=False),
        sa.Column('preferred_learning_areas', sa.JSON(), nullable=False),
        sa.Column('employment_status', sa.String(length=50), nullable=False, server_default='Active'),
        sa.Column('accessibility_preferences', sa.JSON(), nullable=False),
        sa.Column('is_demo', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index(op.f('ix_employee_profiles_id'), 'employee_profiles', ['id'], unique=False)
    op.create_index(op.f('ix_employee_profiles_business_id'), 'employee_profiles', ['business_id'], unique=False)
    op.create_index(op.f('ix_employee_profiles_employee_reference'), 'employee_profiles', ['employee_reference'], unique=False)

    # 6. role_profiles
    op.create_table(
        'role_profiles',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('business_id', sa.String(length=36), sa.ForeignKey('business_profiles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('role_name', sa.String(length=100), nullable=False),
        sa.Column('department', sa.String(length=100), nullable=False),
        sa.Column('required_skills', sa.JSON(), nullable=False),
        sa.Column('optional_skills', sa.JSON(), nullable=False),
        sa.Column('is_demo', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index(op.f('ix_role_profiles_id'), 'role_profiles', ['id'], unique=False)
    op.create_index(op.f('ix_role_profiles_business_id'), 'role_profiles', ['business_id'], unique=False)

    # 7. skill_gaps
    op.create_table(
        'skill_gaps',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('business_id', sa.String(length=36), sa.ForeignKey('business_profiles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('employee_id', sa.String(length=36), sa.ForeignKey('employee_profiles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('role_id', sa.String(length=36), sa.ForeignKey('role_profiles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('current_skill', sa.String(length=100), nullable=True),
        sa.Column('required_skill', sa.String(length=100), nullable=False),
        sa.Column('gap_level', sa.String(length=50), nullable=False, server_default='Medium'),
        sa.Column('recommended_action', sa.Text(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='IDENTIFIED'),
        sa.Column('is_demo', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index(op.f('ix_skill_gaps_id'), 'skill_gaps', ['id'], unique=False)
    op.create_index(op.f('ix_skill_gaps_business_id'), 'skill_gaps', ['business_id'], unique=False)

    # 8. learning_paths
    op.create_table(
        'learning_paths',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('business_id', sa.String(length=36), sa.ForeignKey('business_profiles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('employee_id', sa.String(length=36), sa.ForeignKey('employee_profiles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('target_role', sa.String(length=100), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('skill_sequence', sa.JSON(), nullable=False),
        sa.Column('progress', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='RECOMMENDED'),
        sa.Column('estimated_weeks', sa.Integer(), nullable=False, server_default='4'),
        sa.Column('accessibility_accommodations', sa.JSON(), nullable=False),
        sa.Column('is_demo', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index(op.f('ix_learning_paths_id'), 'learning_paths', ['id'], unique=False)
    op.create_index(op.f('ix_learning_paths_business_id'), 'learning_paths', ['business_id'], unique=False)


def downgrade() -> None:
    op.drop_table('learning_paths')
    op.drop_table('skill_gaps')
    op.drop_table('role_profiles')
    op.drop_table('employee_profiles')
    op.drop_table('supply_chain_risks')
    op.drop_table('supply_items')
    op.drop_table('supplier_documents')
    op.drop_table('suppliers')
