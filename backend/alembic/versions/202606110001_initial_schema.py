"""initial schema

Revision ID: 202606110001
Revises:
Create Date: 2026-06-11 22:00:00.000000
"""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "202606110001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("is_superuser", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )
    op.create_index("ix_users_email", "users", ["email"])

    op.create_table(
        "projects",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("project_name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("owner_id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("owner_id", "project_name", name="uq_projects_owner_name"),
    )
    op.create_index("ix_projects_owner_id", "projects", ["owner_id"])

    op.create_table(
        "samples",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("sample_name", sa.String(length=255), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("project_id", "sample_name", name="uq_samples_project_name"),
    )
    op.create_index("ix_samples_project_id", "samples", ["project_id"])

    op.create_table(
        "genes",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("gene_id", sa.String(length=255), nullable=False),
        sa.Column("chromosome", sa.String(length=64), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("gene_id", name="uq_genes_gene_id"),
    )
    op.create_index("ix_genes_chromosome", "genes", ["chromosome"])
    op.create_index("ix_genes_gene_id", "genes", ["gene_id"])

    op.create_table(
        "variant_files",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("uploaded_by_id", sa.Uuid(), nullable=False),
        sa.Column("original_filename", sa.String(length=512), nullable=False),
        sa.Column("storage_path", sa.String(length=1024), nullable=False),
        sa.Column("size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("checksum_sha256", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="uploaded"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["uploaded_by_id"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_variant_files_project_id", "variant_files", ["project_id"])
    op.create_index("ix_variant_files_status", "variant_files", ["status"])

    op.create_table(
        "variants",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("sample_id", sa.Uuid(), nullable=True),
        sa.Column("chromosome", sa.String(length=64), nullable=False),
        sa.Column("position", sa.BigInteger(), nullable=False),
        sa.Column("reference", sa.Text(), nullable=False),
        sa.Column("alternative", sa.Text(), nullable=False),
        sa.Column("impact", sa.String(length=64), nullable=True),
        sa.Column("gene_id", sa.String(length=255), nullable=True),
        sa.Column("source_file_id", sa.Uuid(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(["gene_id"], ["genes.gene_id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["sample_id"], ["samples.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["source_file_id"], ["variant_files.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_variants_gene_id", "variants", ["gene_id"])
    op.create_index("ix_variants_impact", "variants", ["impact"])
    op.create_index(
        "ix_variants_project_chrom_pos", "variants", ["project_id", "chromosome", "position"]
    )
    op.create_index("ix_variants_sample_id", "variants", ["sample_id"])

    op.create_table(
        "variant_processing_jobs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("file_id", sa.Uuid(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="queued"),
        sa.Column("tool", sa.String(length=64), nullable=False, server_default="vcf-ingest"),
        sa.Column("variants_inserted", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("log", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["file_id"], ["variant_files.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_variant_processing_jobs_file_id", "variant_processing_jobs", ["file_id"])
    op.create_index("ix_variant_processing_jobs_status", "variant_processing_jobs", ["status"])


def downgrade() -> None:
    op.drop_index("ix_variant_processing_jobs_status", table_name="variant_processing_jobs")
    op.drop_index("ix_variant_processing_jobs_file_id", table_name="variant_processing_jobs")
    op.drop_table("variant_processing_jobs")
    op.drop_index("ix_variants_sample_id", table_name="variants")
    op.drop_index("ix_variants_project_chrom_pos", table_name="variants")
    op.drop_index("ix_variants_impact", table_name="variants")
    op.drop_index("ix_variants_gene_id", table_name="variants")
    op.drop_table("variants")
    op.drop_index("ix_variant_files_status", table_name="variant_files")
    op.drop_index("ix_variant_files_project_id", table_name="variant_files")
    op.drop_table("variant_files")
    op.drop_index("ix_genes_gene_id", table_name="genes")
    op.drop_index("ix_genes_chromosome", table_name="genes")
    op.drop_table("genes")
    op.drop_index("ix_samples_project_id", table_name="samples")
    op.drop_table("samples")
    op.drop_index("ix_projects_owner_id", table_name="projects")
    op.drop_table("projects")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
