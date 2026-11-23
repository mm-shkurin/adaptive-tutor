"""Quizzes, questions, and one open attempt."""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0012_quizzes"
down_revision = "0011_chat_line_exam_fields"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "quizzes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("document_name", sa.Text(), nullable=False),
        sa.Column("topic", sa.Text(), nullable=False),
        sa.Column("idempotency_key", sa.String(length=128), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_correct", sa.Integer(), nullable=True),
        sa.Column("last_total", sa.Integer(), nullable=True),
        sa.UniqueConstraint("owner_id", "idempotency_key", name="quizzes_owner_idempotency_key_uq"),
    )
    op.create_index("quizzes_owner_created_idx", "quizzes", ["owner_id", "created_at"])
    op.create_table(
        "quiz_questions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("quiz_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("page", sa.Integer(), nullable=False),
        sa.Column("correct_choice_id", sa.String(length=64), nullable=False),
    )
    op.create_index("quiz_questions_quiz_idx", "quiz_questions", ["quiz_id"])
    op.create_table(
        "quiz_choices",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column(
            "question_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("quiz_questions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
    )
    op.create_index("quiz_choices_question_idx", "quiz_choices", ["question_id"])
    op.create_table(
        "quiz_attempts",
        sa.Column(
            "quiz_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("quizzes.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("current_index", sa.Integer(), nullable=False),
    )
    op.create_table(
        "quiz_answers",
        sa.Column(
            "quiz_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("quizzes.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("scope", sa.String(length=8), primary_key=True),
        sa.Column("question_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("choice_id", sa.String(length=64), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("quiz_answers")
    op.drop_table("quiz_attempts")
    op.drop_index("quiz_choices_question_idx", table_name="quiz_choices")
    op.drop_table("quiz_choices")
    op.drop_index("quiz_questions_quiz_idx", table_name="quiz_questions")
    op.drop_table("quiz_questions")
    op.drop_index("quizzes_owner_created_idx", table_name="quizzes")
    op.drop_table("quizzes")
