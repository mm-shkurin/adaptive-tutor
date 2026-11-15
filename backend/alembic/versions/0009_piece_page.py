"""Starting page stored on each piece."""

from alembic import op
import sqlalchemy as sa

revision = "0009_piece_page"
down_revision = "0008_chat_lines"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("document_pieces", sa.Column("page", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column("document_pieces", "page")
