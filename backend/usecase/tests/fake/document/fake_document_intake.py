from uuid import UUID

from domain.document.document import Document
from usecase.document.list_documents import PAGE_SIZE


class FakeDocumentIntake:
    def __init__(self, bodies: dict[UUID, bytes]):
        self.bodies = bodies
        self.rows: dict[UUID, tuple[UUID, Document]] = {}
        self._order: list[UUID] = []

    async def store(self, owner_id: UUID, document: Document, content: bytes) -> None:
        self.rows[document.id] = (owner_id, document)
        self.bodies[document.id] = content
        self._order.append(document.id)

    async def get(self, owner_id: UUID, document_id: UUID) -> Document | None:
        row = self.rows.get(document_id)
        if row is None or row[0] != owner_id:
            return None
        return row[1]

    async def save(self, document: Document) -> None:
        row = self.rows.get(document.id)
        if row is None:
            return
        self.rows[document.id] = (row[0], document)

    async def next_waiting(self) -> tuple[Document, bytes] | None:
        for document_id in self._order:
            document = self.rows[document_id][1]
            if document.status == "waiting":
                return document, self.bodies[document_id]
        return None

    async def list_page(self, owner_id: UUID, page: int) -> tuple[tuple[Document, ...], bool]:
        owned = [
            self.rows[document_id][1]
            for document_id in reversed(self._order)
            if self.rows[document_id][0] == owner_id
        ]
        start = (page - 1) * PAGE_SIZE
        window = owned[start : start + PAGE_SIZE + 1]
        return tuple(window[:PAGE_SIZE]), len(window) > PAGE_SIZE
