from uuid import UUID

from domain.document.document import Document
from usecase.document.ports import DocumentIntake


class ReadDocument:
    def __init__(self, intake: DocumentIntake):
        self.intake = intake

    async def read(self, owner_id: UUID, document_id: UUID) -> Document:
        found = await self.intake.get(owner_id, document_id)
        if found is None:
            raise KeyError(document_id)
        return found
