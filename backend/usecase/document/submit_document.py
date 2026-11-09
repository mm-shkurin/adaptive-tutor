from dataclasses import dataclass
from uuid import UUID

from domain.document.document import Document
from usecase.document.errors import DuplicateSubmission
from usecase.document.ports import DocumentIntake, UploadRateLimit, VirusCheck


@dataclass(frozen=True)
class AcceptedSubmission:
    document: Document
    created: bool


class SubmitDocument:
    def __init__(self, intake: DocumentIntake, rates: UploadRateLimit, virus: VirusCheck):
        self.intake = intake
        self.rates = rates
        self.virus = virus

    async def submit(
        self, owner_id: UUID, name: str, content: bytes, submission_key: str
    ) -> AcceptedSubmission:
        await self.virus.clear(content)
        existing = await self.intake.find_by_key(owner_id, submission_key)
        if existing is not None:
            return AcceptedSubmission(existing, created=False)
        await self.rates.try_accept(owner_id)
        document = Document.accepted(name, len(content))
        try:
            await self.intake.store(owner_id, document, content, submission_key)
        except DuplicateSubmission:
            await self.rates.release(owner_id)
            return AcceptedSubmission(
                await self._replay(owner_id, submission_key), created=False
            )
        except Exception:
            await self.rates.release(owner_id)
            raise
        return AcceptedSubmission(document, created=True)

    async def _replay(self, owner_id: UUID, submission_key: str) -> Document:
        existing = await self.intake.find_by_key(owner_id, submission_key)
        if existing is None:
            raise DuplicateSubmission()
        return existing
