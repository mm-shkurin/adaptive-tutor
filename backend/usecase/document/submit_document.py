from uuid import UUID

from domain.document.document import Document
from usecase.document.ports import DocumentIntake, UploadRateLimit


class SubmitDocument:
    def __init__(self, intake: DocumentIntake, rates: UploadRateLimit):
        self.intake = intake
        self.rates = rates

    async def submit(self, owner_id: UUID, name: str, content: bytes) -> Document:
        await self.rates.try_accept(owner_id)
        document = Document.accepted(name, len(content))
        try:
            await self.intake.store(owner_id, document, content)
        except Exception:
            await self.rates.release(owner_id)
            raise
        return document
