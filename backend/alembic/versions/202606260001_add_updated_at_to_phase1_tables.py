"""add updated_at to phase 1 tables

Revision ID: 202606260001
Revises: 202606110001
Create Date: 2026-06-26 00:00:00.000000
"""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "202606260001"
down_revision = "202606110001"
branch_labels = None
depends_on = None

PHASE1_TABLES = (
    "users",
    "projects",
    "samples",
    "genes",
    "variant_files",
    "variant_processing_jobs",
    "variants",
)


def upgrade() -> None:
    for table_name in PHASE1_TABLES:
        op.add_column(
            table_name,
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.text("now()"),
            ),
        )


def downgrade() -> None:
    for table_name in reversed(PHASE1_TABLES):
        op.drop_column(table_name, "updated_at")
