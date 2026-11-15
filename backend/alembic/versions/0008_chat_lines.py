"""Lines of a chat reply."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0008_chat_lines"
down_revision = "0007_chats"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "chat_lines",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("chat_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("chats.id"), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("role", sa.String(length=16), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("model", sa.Text(), nullable=True),
        sa.Column("mode", sa.String(length=32), nullable=True),
        sa.Column("kind", sa.String(length=16), nullable=True),
        sa.Column("page", sa.Integer(), nullable=True),
        sa.Column("sources", postgresql.JSONB(), nullable=False),
    )
    op.create_index("chat_lines_chat_position_idx", "chat_lines", ["chat_id", "position"], unique=True)


def downgrade() -> None:
    op.drop_index("chat_lines_chat_position_idx", table_name="chat_lines")
    op.drop_table("chat_lines")
