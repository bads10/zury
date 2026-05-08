"""initial

Revision ID: 0001
Revises:
Create Date: 2026-05-08 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "garments",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("seller_id", sa.String(), nullable=False),
        sa.Column("seller_slug", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("category", sa.String(), nullable=True),
        sa.Column("image_url", sa.String(), nullable=True),
        sa.Column("meta", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_garments_seller_id", "garments", ["seller_id"])
    op.create_index("ix_garments_seller_slug", "garments", ["seller_slug"])

    op.create_table(
        "jobs",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("celery_task_id", sa.String(), nullable=True),
        sa.Column("garment_id", sa.String(), nullable=False),
        sa.Column("seller_id", sa.String(), nullable=False),
        sa.Column("fitzpatrick", sa.Integer(), nullable=False),
        sa.Column("selfie_path", sa.String(), nullable=True),
        sa.Column(
            "status",
            sa.Enum("pending", "processing", "done", "failed", name="jobstatus"),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("progress", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("result_url", sa.String(), nullable=True),
        sa.Column("estimated_seconds", sa.Integer(), nullable=False, server_default="10"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("jobs")
    op.drop_index("ix_garments_seller_slug", table_name="garments")
    op.drop_index("ix_garments_seller_id", table_name="garments")
    op.drop_table("garments")
    op.execute("DROP TYPE IF EXISTS jobstatus")
