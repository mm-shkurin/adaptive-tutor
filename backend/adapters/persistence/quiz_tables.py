from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from adapters.persistence.tables import Base


class QuizChoiceRow(Base):
    __tablename__ = "quiz_choices"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    question_id: Mapped[UUID] = mapped_column(
        ForeignKey("quiz_questions.id", ondelete="CASCADE"), index=True
    )
    position: Mapped[int] = mapped_column(Integer)
    body: Mapped[str] = mapped_column(Text)


class QuizQuestionRow(Base):
    __tablename__ = "quiz_questions"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    quiz_id: Mapped[UUID] = mapped_column(ForeignKey("quizzes.id", ondelete="CASCADE"), index=True)
    position: Mapped[int] = mapped_column(Integer)
    body: Mapped[str] = mapped_column(Text)
    page: Mapped[int | None] = mapped_column(Integer)
    slide: Mapped[int | None] = mapped_column(Integer)
    correct_choice_id: Mapped[str] = mapped_column(String(64))
    choices: Mapped[list[QuizChoiceRow]] = relationship(
        order_by=QuizChoiceRow.position,
        cascade="all, delete-orphan",
    )


class QuizAnswerRow(Base):
    __tablename__ = "quiz_answers"

    quiz_id: Mapped[UUID] = mapped_column(ForeignKey("quizzes.id", ondelete="CASCADE"), primary_key=True)
    scope: Mapped[str] = mapped_column(String(8), primary_key=True)
    question_id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    choice_id: Mapped[str] = mapped_column(String(64))


class QuizAttemptRow(Base):
    __tablename__ = "quiz_attempts"

    quiz_id: Mapped[UUID] = mapped_column(ForeignKey("quizzes.id", ondelete="CASCADE"), primary_key=True)
    current_index: Mapped[int] = mapped_column(Integer)


class QuizRow(Base):
    __tablename__ = "quizzes"
    __table_args__ = (
        UniqueConstraint("owner_id", "idempotency_key", name="quizzes_owner_idempotency_key_uq"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    owner_id: Mapped[UUID] = mapped_column(Uuid, index=True)
    document_id: Mapped[UUID] = mapped_column(Uuid)
    document_name: Mapped[str] = mapped_column(Text)
    topic: Mapped[str] = mapped_column(Text)
    idempotency_key: Mapped[str] = mapped_column(String(128))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_correct: Mapped[int | None] = mapped_column(Integer)
    last_total: Mapped[int | None] = mapped_column(Integer)
    questions: Mapped[list[QuizQuestionRow]] = relationship(
        order_by=QuizQuestionRow.position,
        cascade="all, delete-orphan",
    )
    answers: Mapped[list[QuizAnswerRow]] = relationship(cascade="all, delete-orphan")
    attempt: Mapped[QuizAttemptRow | None] = relationship(cascade="all, delete-orphan", uselist=False)
