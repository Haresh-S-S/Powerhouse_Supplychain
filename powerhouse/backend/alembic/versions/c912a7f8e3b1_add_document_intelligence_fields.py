"""add_document_intelligence_fields

Revision ID: c912a7f8e3b1
Revises: ba01a4b9120a
Create Date: 2026-09-07 11:10:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c912a7f8e3b1'
down_revision: Union[str, None] = 'ba01a4b9120a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('documents', schema=None) as batch_op:
        batch_op.add_column(sa.Column('content_hash', sa.String(length=64), nullable=True))
        batch_op.add_column(sa.Column('analysis_status', sa.String(length=50), nullable=False, server_default='Uploaded'))
        batch_op.add_column(sa.Column('extracted_data', sa.String(length=4000), nullable=True))
        batch_op.create_index(batch_op.f('ix_documents_content_hash'), ['content_hash'], unique=False)


def downgrade() -> None:
    with op.batch_alter_table('documents', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_documents_content_hash'))
        batch_op.drop_column('extracted_data')
        batch_op.drop_column('analysis_status')
        batch_op.drop_column('content_hash')
