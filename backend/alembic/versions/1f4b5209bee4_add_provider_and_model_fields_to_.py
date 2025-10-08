"""Add provider and model fields to personas

Revision ID: 1f4b5209bee4
Revises: a254c2db6d04
Create Date: 2025-10-08 16:12:51.004593

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1f4b5209bee4'
down_revision: Union[str, None] = 'a254c2db6d04'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add provider and model columns to personas table
    op.add_column('personas', sa.Column('provider', sa.String(50), nullable=True, default='auto'))
    op.add_column('personas', sa.Column('model', sa.String(100), nullable=True))


def downgrade() -> None:
    # Remove provider and model columns from personas table
    op.drop_column('personas', 'provider')
    op.drop_column('personas', 'model')