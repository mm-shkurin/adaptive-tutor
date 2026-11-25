"""Slide position on indexed document pieces."""

import sqlalchemy as sa
from alembic import op

revision = "0015_document_piece_slide"
down_revision = "0014_presentation_store_support"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("document_pieces", sa.Column("slide", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column("document_pieces", "slide")