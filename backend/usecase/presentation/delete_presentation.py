from uuid import UUID

from usecase.document.ports import DocumentIntake, PieceIndex
from usecase.presentation.errors import PresentationNotFound
from usecase.presentation.ports import PresentationStore


class DeletePresentation:
    def __init__(self, presentations: PresentationStore, intake: DocumentIntake, pieces: PieceIndex):
        self.presentations = presentations
        self.intake = intake
        self.pieces = pieces

    async def delete(self, owner_id: UUID, presentation_id: UUID) -> None:
        found = await self.presentations.get(owner_id, presentation_id)
        if found is None:
            raise PresentationNotFound()
        await self.presentations.remove(owner_id, presentation_id)
        await self.intake.remove(owner_id, presentation_id)
        await self.pieces.replace(presentation_id, (), "")