"""Exam choice fields on chat lines."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0011_chat_line_exam_fields"
down_revision = "0010_chat_attempts"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "chat_lines",
        sa.Column("choices", postgresql.JSONB(), nullable=False, server_default=sa.text("'[]'::jsonb")),
    )
    op.add_column("chat_lines", sa.Column("choice_id", sa.String(length=64), nullable=True))
    op.add_column("chat_lines", sa.Column("correct", sa.Boolean(), nullable=True))
    op.add_column(
        "chat_lines", sa.Column("supported_choice_id", sa.String(length=64), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("chat_lines", "supported_choice_id")
    op.drop_column("chat_lines", "correct")
    op.drop_column("chat_lines", "choice_id")
    op.drop_column("chat_lines", "choices")
