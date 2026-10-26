from uuid import UUID

from domain.document.document import Document
from usecase.document.errors import DuplicateSubmission
from usecase.document.list_documents import PAGE_SIZE


class FakeDocumentIntake:
    def __init__(self, bodies: dict[UUID, bytes]):
        self.bodies = bodies
        self.rows: dict[UUID, tuple[UUID, Document]] = {}
        self._order: list[UUID] = []
        self._keys: dict[tuple[UUID, str], UUID] = {}

    async def find_by_key(self, owner_id: UUID, submission_key: str) -> Document | None:
        document_id = self._keys.get((owner_id, submission_key))
        if document_id is None:
            return None
        row = self.rows.get(document_id)
        return None if row is None else row[1]

    async def store(
        self, owner_id: UUID, document: Document, content: bytes, submission_key: str
    ) -> None:
        key = (owner_id, submission_key)
        if key in self._keys:
            raise DuplicateSubmission()
        self._keys[key] = document.id
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
