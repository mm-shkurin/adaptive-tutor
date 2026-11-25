"""Presentation decks, slides, and document kind."""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0013_presentations"
down_revision = "0012_quizzes"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("documents", sa.Column("kind", sa.String(length=16), server_default="pdf", nullable=False))
    op.create_table(
        "presentations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("piece_count", sa.Integer(), nullable=True),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("presentations_owner_created_idx", "presentations", ["owner_id", "created_at"])
    op.create_table(
        "presentation_slides",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "presentation_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("presentations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("source", sa.String(length=16), nullable=False),
        sa.Column("text", sa.Text(), nullable=False, server_default=""),
        sa.Column("formula_phrase", sa.Text(), nullable=True),
        sa.Column("formula_latex", sa.Text(), nullable=True),
        sa.Column("empty", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("pdf_document_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("pdf_page", sa.Integer(), nullable=True),
    )
    op.create_index("presentation_slides_deck_idx", "presentation_slides", ["presentation_id"])


def downgrade() -> None:
    op.drop_index("presentation_slides_deck_idx", table_name="presentation_slides")
    op.drop_table("presentation_slides")
    op.drop_index("presentations_owner_created_idx", table_name="presentations")
    op.drop_table("presentations")
    op.drop_column("documents", "kind")