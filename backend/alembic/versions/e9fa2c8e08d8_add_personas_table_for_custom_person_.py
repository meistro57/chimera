"""Add personas table for custom person creation

Revision ID: e9fa2c8e08d8
Revises: fd92c5af2c65
Create Date: 2025-10-08 10:38:35.475273

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e9fa2c8e08d8'
down_revision: Union[str, None] = 'fd92c5af2c65'
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