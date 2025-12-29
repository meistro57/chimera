# backend/alembic/versions/b31e9e8b17cf_align_core_models_with_schema.py
"""Align core models with schema

Revision ID: b31e9e8b17cf
Revises: 1f4b5209bee4
Create Date: 2025-10-08 20:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b31e9e8b17cf"
down_revision: Union[str, None] = "1f4b5209bee4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema to match current core models."""
    # Add missing authentication field to users
    with op.batch_alter_table("users") as batch_op:
        batch_op.add_column(sa.Column("hashed_password", sa.Text(), nullable=True))

    # Add sharing controls to conversations
    with op.batch_alter_table("conversations") as batch_op:
        batch_op.add_column(
            sa.Column("is_public", sa.Boolean(), nullable=False, server_default=sa.false())
        )
        batch_op.add_column(sa.Column("share_token", sa.String(length=255), nullable=True))

    # Align message metadata naming with the model
    with op.batch_alter_table("messages") as batch_op:
        batch_op.alter_column(
            "message_metadata",
            new_column_name="metadata",
            existing_type=sa.JSON(),
            existing_nullable=True,
        )


def downgrade() -> None:
    """Revert schema changes for core models."""
    with op.batch_alter_table("messages") as batch_op:
        batch_op.alter_column(
            "metadata",
            new_column_name="message_metadata",
            existing_type=sa.JSON(),
            existing_nullable=True,
        )

    with op.batch_alter_table("conversations") as batch_op:
        batch_op.drop_column("share_token")
        batch_op.drop_column("is_public")

    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_column("hashed_password")
