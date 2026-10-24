"""initial_schema

Revision ID: 23314f03d4c0
Revises: 
Create Date: 2026-06-06 21:08:45.755432

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '23314f03d4c0'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('documents',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('file_name', sa.String(), nullable=True),
    sa.Column('document_type', sa.String(), nullable=True),
    sa.Column('file_path', sa.String(), nullable=True),
    sa.Column('extracted_text', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True),
              server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_documents_id'), 'documents', ['id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_documents_id'), table_name='documents')
    op.drop_table('documents')
