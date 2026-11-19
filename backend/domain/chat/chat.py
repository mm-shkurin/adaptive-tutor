from dataclasses import dataclass, replace
from uuid import UUID, uuid4

from domain.chat.line import Line
from domain.chat.source import Source
from domain.document.document import Document

NOT_ASKABLE_NOTICE = "Материал пока нельзя спросить."


class DocumentNotReady(Exception):
    """A chat binds only a ready PDF."""


class NotAskable(Exception):
    """This material has no vectors yet."""


@dataclass(frozen=True)
class Chat:
    id: UUID
    document_id: UUID
    document_name: str
    vectors_ready: bool
    lines: tuple[Line, ...] = ()

    @staticmethod
    def bound_to(document: Document) -> "Chat":
        if not document.is_ready():
            raise DocumentNotReady()
        return Chat(
            id=uuid4(),
            document_id=document.id,
            document_name=document.name,
            vectors_ready=False,
        )

    @staticmethod
    def stored(
        chat_id: UUID,
        document_id: UUID,
        document_name: str,
        lines: tuple[Line, ...] = (),
    ) -> "Chat":
        return Chat(chat_id, document_id, document_name, vectors_ready=False, lines=lines)

    def with_vectors(self, ready: bool) -> "Chat":
        return replace(self, vectors_ready=ready)

    def preview(self) -> str | None:
        spoken = tuple(line.text for line in self.lines if line.role == "person")
        if not spoken:
            return None
        return spoken[-1]

    def askable(self) -> bool:
        return self.vectors_ready

    def notice(self) -> str | None:
        if self.vectors_ready:
            return None
        return NOT_ASKABLE_NOTICE

    def record_grounded(
        self,
        question: str,
        model: str,
        mode: str,
        sources: tuple[Source, ...],
        tutor_text: str,
    ) -> tuple["Chat", tuple[Line, Line]]:
        person = Line.person(question)
        tutor = Line.grounded(tutor_text, model, mode, sources)
        return replace(self, lines=self.lines + (person, tutor)), (person, tutor)

    def record_missing(self, question: str, mode: str) -> tuple["Chat", tuple[Line, Line]]:
        person = Line.person(question)
        tutor = Line.missing(mode)
        return replace(self, lines=self.lines + (person, tutor)), (person, tutor)

    def record_failed(self, question: str) -> tuple["Chat", tuple[Line, ...]]:
        person = Line.person(question)
        return replace(self, lines=self.lines + (person,)), (person,)

    def with_appended(self, lines: tuple[Line, ...]) -> "Chat":
        return replace(self, lines=self.lines + lines)
