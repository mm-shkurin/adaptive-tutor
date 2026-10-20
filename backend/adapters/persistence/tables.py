from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, LargeBinary, String, Text, Uuid
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class AccountRow(Base):
    __tablename__ = "accounts"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    yandex_subject: Mapped[str] = mapped_column(String(255), unique=True)
    email: Mapped[str] = mapped_column(String(320))
    provider_name: Mapped[str] = mapped_column(Text)
    profile_name: Mapped[str | None] = mapped_column(String(60))
    avatar_key: Mapped[UUID | None] = mapped_column(Uuid)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    def to_domain(self):
        from domain.account.account import Account

        return Account(
            id=self.id,
            yandex_subject=self.yandex_subject,
            email=self.email,
            provider_name=self.provider_name,
            created_at=self.created_at,
            profile_name=self.profile_name,
            avatar_key=self.avatar_key,
        )

    def apply(self, account) -> None:
        self.email = account.email
        self.provider_name = account.provider_name
        self.profile_name = account.profile_name
        self.avatar_key = account.avatar_key


class AvatarRow(Base):
    __tablename__ = "avatars"

    key: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    owner_id: Mapped[UUID] = mapped_column(index=True)
    content_type: Mapped[str] = mapped_column(String(32))
    body: Mapped[bytes] = mapped_column(LargeBinary)
