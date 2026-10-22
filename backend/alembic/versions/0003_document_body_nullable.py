"""make document body nullable

Revision ID: 0003
Revises: 0002
Create Date: 2026-10-22

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0003'
down_revision: Union[str, None] = '0002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('documents') as batch_op:
        batch_op.alter_column('body',
                              existing_type=sa.LargeBinary(),
                              nullable=True)


def downgrade() -> None:
    with op.batch_alter_table('documents') as batch_op:
        batch_op.alter_column('body',
                              existing_type=sa.LargeBinary(),
                              nullable=False)
