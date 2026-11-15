from dataclasses import dataclass
from uuid import UUID, uuid4

from domain.document.document import Document

NOT_ASKABLE_NOTICE = "Материал пока нельзя спросить."


class DocumentNotReady(Exception):
    """A chat binds only a ready PDF."""


@dataclass(frozen=True)
class Chat:
    id: UUID
    document_id: UUID
    document_name: str
    vectors_ready: bool
    lines: tuple = ()

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
    def stored(chat_id: UUID, document_id: UUID, document_name: str) -> "Chat":
        return Chat(chat_id, document_id, document_name, vectors_ready=False)

    def preview(self) -> str | None:
        return None

    def askable(self) -> bool:
        return self.vectors_ready

    def notice(self) -> str | None:
        if self.vectors_ready:
            return None
        return NOT_ASKABLE_NOTICE
