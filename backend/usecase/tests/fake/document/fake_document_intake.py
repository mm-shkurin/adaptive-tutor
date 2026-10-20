from uuid import UUID

from domain.document.document import Document


class FakeDocumentIntake:
    def __init__(self, bodies: dict[UUID, bytes]):
        self.bodies = bodies
        self.rows: dict[UUID, tuple[UUID, Document]] = {}

    async def store(self, owner_id: UUID, document: Document, content: bytes) -> None:
        self.rows[document.id] = (owner_id, document)
        self.bodies[document.id] = content

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
        for document_id, row in self.rows.items():
            document = row[1]
            if document.status == "waiting":
                return document, self.bodies[document_id]
        return None
