from uuid import UUID

from domain.presentation.presentation import Presentation
from usecase.presentation.errors import PresentationNotFound
from usecase.presentation.ports import PresentationStore


class GetPresentation:
    def __init__(self, presentations: PresentationStore):
        self.presentations = presentations

    async def open(self, owner_id: UUID, presentation_id: UUID) -> Presentation:
        found = await self.presentations.get(owner_id, presentation_id)
        if found is None:
            raise PresentationNotFound()
        return found