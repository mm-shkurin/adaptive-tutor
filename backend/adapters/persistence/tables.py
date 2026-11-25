from datetime import datetime
from uuid import UUID

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, LargeBinary, String, Text, UniqueConstraint, Uuid
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


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


class DocumentRow(Base):
    __tablename__ = "documents"
    __table_args__ = (UniqueConstraint("owner_id", "idempotency_key", name="documents_owner_idempotency_key_uq"),)

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    owner_id: Mapped[UUID] = mapped_column(index=True)
    idempotency_key: Mapped[str] = mapped_column(String(255))
    name: Mapped[str] = mapped_column(Text)
    kind: Mapped[str] = mapped_column(String(16), server_default="pdf")
    size_bytes: Mapped[int] = mapped_column(Integer)
    page_count: Mapped[int | None] = mapped_column(Integer)
    piece_count: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(32))
    error: Mapped[str | None] = mapped_column(Text)
    body: Mapped[bytes | None] = mapped_column(LargeBinary)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    def to_domain(self):
        from domain.document.document import Document

        return Document(
            id=self.id,
            name=self.name,
            kind=self.kind,
            size_bytes=self.size_bytes,
            page_count=self.page_count,
            piece_count=self.piece_count,
            status=self.status,
            error=self.error,
        )

    def apply(self, document) -> None:
        chosen = self.to_domain().prefer_terminal(document)
        self.name = chosen.name
        self.kind = chosen.kind
        self.size_bytes = chosen.size_bytes
        self.page_count = chosen.page_count
        self.piece_count = chosen.piece_count
        self.status = chosen.status
        self.error = chosen.error


class DocumentPieceRow(Base):
    __tablename__ = "document_pieces"

    document_id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    ordinal: Mapped[int] = mapped_column(Integer, primary_key=True)
    body: Mapped[str] = mapped_column(Text)
    page: Mapped[int | None] = mapped_column(Integer)


class DocumentExtractionRow(Base):
    __tablename__ = "document_extractions"

    document_id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    text: Mapped[str] = mapped_column(Text)


class ChatRow(Base):
    __tablename__ = "chats"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    owner_id: Mapped[UUID] = mapped_column(Uuid, index=True)
    document_id: Mapped[UUID] = mapped_column(Uuid, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    lines: Mapped[list["ChatLineRow"]] = relationship(
        order_by="ChatLineRow.position",
        cascade="all, delete-orphan",
    )


class ChatLineRow(Base):
    __tablename__ = "chat_lines"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    chat_id: Mapped[UUID] = mapped_column(ForeignKey("chats.id"), index=True)
    position: Mapped[int] = mapped_column(Integer)
    role: Mapped[str] = mapped_column(String(16))
    body: Mapped[str] = mapped_column(Text)
    model: Mapped[str | None] = mapped_column(Text)
    mode: Mapped[str | None] = mapped_column(String(32))
    kind: Mapped[str | None] = mapped_column(String(16))
    page: Mapped[int | None] = mapped_column(Integer)
    sources: Mapped[list] = mapped_column(JSON)
    choices: Mapped[list] = mapped_column(JSON, default=list)
    choice_id: Mapped[str | None] = mapped_column(String(64))
    correct: Mapped[bool | None] = mapped_column(Boolean)
    supported_choice_id: Mapped[str | None] = mapped_column(String(64))

    def to_domain(self):
        from domain.chat.choice import Choice
        from domain.chat.line import Line
        from domain.chat.source import Source

        return Line(
            id=self.id,
            role=self.role,
            text=self.body,
            model=self.model,
            mode=self.mode,
            kind=self.kind,
            page=self.page,
            sources=tuple(Source(page=item["page"], text=item["text"]) for item in self.sources),
            choices=tuple(Choice(item["id"], item["text"]) for item in (self.choices or ())),
            choice_id=self.choice_id,
            correct=self.correct,
            supported_choice_id=self.supported_choice_id,
        )

    @staticmethod
    def from_line(chat_id: UUID, position: int, line) -> "ChatLineRow":
        return ChatLineRow(
            id=line.id,
            chat_id=chat_id,
            position=position,
            role=line.role,
            body=line.text,
            model=line.model,
            mode=line.mode,
            kind=line.kind,
            page=line.page,
            sources=[source.json() for source in line.sources],
            choices=[choice.json() for choice in line.choices],
            choice_id=line.choice_id,
            correct=line.correct,
            supported_choice_id=line.supported_choice_id,
        )


class ChatAttemptRow(Base):
    __tablename__ = "chat_attempts"

    chat_id: Mapped[UUID] = mapped_column(ForeignKey("chats.id"), primary_key=True)
    attempt_key: Mapped[str] = mapped_column(String(255), primary_key=True)
    line_ids: Mapped[list] = mapped_column(JSON)
    error_code: Mapped[str | None] = mapped_column(String(64))
    error_message: Mapped[str | None] = mapped_column(Text)
