"""When a quiz attempt is finished."""

import sqlalchemy as sa
from alembic import op

revision = "0017_quiz_finished_at"
down_revision = "0016_quiz_question_slide"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("quizzes", sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column("quizzes", "finished_at")