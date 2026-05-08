"""sellers

Revision ID: 0002
Revises: 0001
Create Date: 2026-05-08 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "sellers",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("hashed_password", sa.String(), nullable=False),
        sa.Column("slug", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("location", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_sellers_email", "sellers", ["email"], unique=True)
    op.create_index("ix_sellers_slug", "sellers", ["slug"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_sellers_slug", table_name="sellers")
    op.drop_index("ix_sellers_email", table_name="sellers")
    op.drop_table("sellers")
