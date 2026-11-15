"""Idempotent chat send attempts."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0010_chat_attempts"
down_revision = "0009_piece_page"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "chat_attempts",
        sa.Column("chat_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("chats.id"), nullable=False),
        sa.Column("attempt_key", sa.String(length=255), nullable=False),
        sa.Column("line_ids", postgresql.JSONB(), nullable=False),
        sa.Column("error_code", sa.String(length=64), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("chat_id", "attempt_key"),
    )


def downgrade() -> None:
    op.drop_table("chat_attempts")
