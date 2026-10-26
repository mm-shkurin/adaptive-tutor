from uuid import UUID

from domain.document.document import Document
from usecase.document.ports import DocumentIntake

PAGE_SIZE = 50


class ListDocuments:
    def __init__(self, intake: DocumentIntake):
        self.intake = intake

    async def list(self, owner_id: UUID, page: int) -> tuple[tuple[Document, ...], bool]:
        return await self.intake.list_page(owner_id, max(page, 1))
