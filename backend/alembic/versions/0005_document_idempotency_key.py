"""Document Idempotency-Key uniqueness per owner.

Revision ID: 0005
Revises: 0004
Create Date: 2026-10-26

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0005"
down_revision: Union[str, None] = "0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "documents",
        sa.Column("idempotency_key", sa.String(length=255), nullable=True),
    )
    op.execute("UPDATE documents SET idempotency_key = id::text WHERE idempotency_key IS NULL")
    with op.batch_alter_table("documents") as batch_op:
        batch_op.alter_column("idempotency_key", existing_type=sa.String(255), nullable=False)
        batch_op.create_unique_constraint(
            "documents_owner_idempotency_key_uq",
            ["owner_id", "idempotency_key"],
        )


def downgrade() -> None:
    with op.batch_alter_table("documents") as batch_op:
        batch_op.drop_constraint("documents_owner_idempotency_key_uq", type_="unique")
        batch_op.drop_column("idempotency_key")
