from datetime import datetime
from uuid import UUID

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, LargeBinary, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from adapters.persistence.tables import Base


class PresentationRow(Base):
    __tablename__ = "presentations"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    owner_id: Mapped[UUID] = mapped_column(Uuid, index=True)
    title: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(16))
    piece_count: Mapped[int | None] = mapped_column(Integer)
    error: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    slides: Mapped[list["PresentationSlideRow"]] = relationship(
        order_by="PresentationSlideRow.position",
        cascade="all, delete-orphan",
    )


class PresentationSlideRow(Base):
    __tablename__ = "presentation_slides"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    presentation_id: Mapped[UUID] = mapped_column(
        ForeignKey("presentations.id", ondelete="CASCADE"), index=True
    )
    position: Mapped[int] = mapped_column(Integer)
    source: Mapped[str] = mapped_column(String(16))
    text: Mapped[str] = mapped_column(Text)
    formula_phrase: Mapped[str | None] = mapped_column(Text)
    formula_latex: Mapped[str | None] = mapped_column(Text)
    empty: Mapped[bool] = mapped_column(Boolean)
    pdf_document_id: Mapped[UUID | None] = mapped_column(Uuid)
    pdf_page: Mapped[int | None] = mapped_column(Integer)


class PresentationSlideBytesRow(Base):
    __tablename__ = "presentation_slide_bytes"

    presentation_id: Mapped[UUID] = mapped_column(
        ForeignKey("presentations.id", ondelete="CASCADE"), primary_key=True
    )
    slide_id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    body: Mapped[bytes] = mapped_column(LargeBinary)


class PresentationAddKeyRow(Base):
    __tablename__ = "presentation_add_keys"

    owner_id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    presentation_id: Mapped[UUID] = mapped_column(
        ForeignKey("presentations.id", ondelete="CASCADE"), primary_key=True
    )
    key: Mapped[str] = mapped_column(String(255), primary_key=True)
    snapshot: Mapped[dict] = mapped_column(JSON)


class PresentationIndexKeyRow(Base):
    __tablename__ = "presentation_index_keys"

    owner_id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    presentation_id: Mapped[UUID] = mapped_column(
        ForeignKey("presentations.id", ondelete="CASCADE"), primary_key=True
    )
    key: Mapped[str] = mapped_column(String(255), primary_key=True)
    snapshot: Mapped[dict] = mapped_column(JSON)