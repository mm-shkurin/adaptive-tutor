"""Accounts and their photos."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_accounts"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "accounts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("yandex_subject", sa.String(255), nullable=False),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("provider_name", sa.Text(), nullable=False),
        sa.Column("profile_name", sa.String(60), nullable=True),
        sa.Column("avatar_key", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("accounts_yandex_subject_key", "accounts", ["yandex_subject"], unique=True)
    op.create_table(
        "avatars",
        sa.Column("key", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("content_type", sa.String(32), nullable=False),
        sa.Column("body", sa.LargeBinary(), nullable=False),
    )
    op.create_index("avatars_owner_id_idx", "avatars", ["owner_id"])


def downgrade() -> None:
    op.drop_index("avatars_owner_id_idx", table_name="avatars")
    op.drop_table("avatars")
    op.drop_index("accounts_yandex_subject_key", table_name="accounts")
    op.drop_table("accounts")
