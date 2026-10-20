from uuid import UUID

from domain.document.document import Document
from usecase.document.ports import DocumentIntake


class SubmitDocument:
    def __init__(self, intake: DocumentIntake):
        self.intake = intake

    async def submit(self, owner_id: UUID, name: str, content: bytes) -> Document:
        raise NotImplementedError()
