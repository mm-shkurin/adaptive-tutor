from uuid import UUID

from domain.document.document import Document
from usecase.document.ports import DocumentIntake


class PostgresDocumentIntake(DocumentIntake):
    def __init__(self, sessions):
        self._sessions = sessions

    async def store(self, owner_id: UUID, document: Document, content: bytes) -> None:
        raise NotImplementedError()

    async def get(self, owner_id: UUID, document_id: UUID) -> Document | None:
        raise NotImplementedError()

    async def save(self, document: Document) -> None:
        raise NotImplementedError()

    async def next_waiting(self) -> tuple[Document, bytes] | None:
        raise NotImplementedError()
