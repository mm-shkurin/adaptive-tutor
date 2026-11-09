"""Store document names as text so a 255-grapheme name is not cut mid-letter.

Revision ID: 0006
Revises: 0005
Create Date: 2026-11-09

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0006"
down_revision: Union[str, None] = "0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("documents") as batch_op:
        batch_op.alter_column(
            "name",
            existing_type=sa.String(255),
            type_=sa.Text(),
            existing_nullable=False,
        )


def downgrade() -> None:
    with op.batch_alter_table("documents") as batch_op:
        batch_op.alter_column(
            "name",
            existing_type=sa.Text(),
            type_=sa.String(255),
            existing_nullable=False,
        )
