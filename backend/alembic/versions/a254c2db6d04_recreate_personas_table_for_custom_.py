"""Recreate personas table for custom personas

Revision ID: a254c2db6d04
Revises: f47ba30030c3
Create Date: 2025-10-08 15:47:59.985835

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a254c2db6d04'
down_revision: Union[str, None] = 'f47ba30030c3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create personas table
    op.create_table(
        "personas",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("display_name", sa.String(length=100), nullable=False),
        sa.Column("system_prompt", sa.String(length=2000), nullable=False),
        sa.Column("temperature", sa.Float(), nullable=True),
        sa.Column("avatar_color", sa.String(length=20), nullable=True),
        sa.Column("personality_traits", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name")
    )


def downgrade() -> None:
    op.drop_table("personas")