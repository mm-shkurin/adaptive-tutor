"""Timestamps for chat lines used by progress sessions."""

import sqlalchemy as sa
from alembic import op

revision = "0018_chat_line_created_at"
down_revision = "0017_quiz_finished_at"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "chat_lines",
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.execute(
        """
        UPDATE chat_lines AS line
        SET created_at = chat.created_at
        FROM chats AS chat
        WHERE line.chat_id = chat.id AND line.created_at IS NULL
        """
    )
    op.alter_column("chat_lines", "created_at", nullable=False)


def downgrade() -> None:
    op.drop_column("chat_lines", "created_at")
