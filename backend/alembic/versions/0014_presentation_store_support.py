"""Presentation slide bytes and idempotency snapshots."""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0014_presentation_store_support"
down_revision = "0013_presentations"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "presentation_slide_bytes",
        sa.Column(
            "presentation_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("presentations.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("slide_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("body", sa.LargeBinary(), nullable=False),
    )
    op.create_table(
        "presentation_add_keys",
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "presentation_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("presentations.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("key", sa.String(length=255), primary_key=True),
        sa.Column("snapshot", postgresql.JSON(astext_type=sa.Text()), nullable=False),
    )
    op.create_table(
        "presentation_index_keys",
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "presentation_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("presentations.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("key", sa.String(length=255), primary_key=True),
        sa.Column("snapshot", postgresql.JSON(astext_type=sa.Text()), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("presentation_index_keys")
    op.drop_table("presentation_add_keys")
    op.drop_table("presentation_slide_bytes")