"""Slide citation on quiz questions."""

import sqlalchemy as sa
from alembic import op

revision = "0016_quiz_question_slide"
down_revision = "0015_document_piece_slide"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("quiz_questions", sa.Column("slide", sa.Integer(), nullable=True))
    op.alter_column("quiz_questions", "page", existing_type=sa.Integer(), nullable=True)


def downgrade() -> None:
    op.alter_column("quiz_questions", "page", existing_type=sa.Integer(), nullable=False)
    op.drop_column("quiz_questions", "slide")