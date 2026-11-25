from uuid import UUID

from domain.presentation.presentation import Presentation
from usecase.document.ports import DocumentIntake
from usecase.presentation.materials import material_row
from usecase.presentation.ports import PresentationStore


class CreatePresentation:
    def __init__(self, presentations: PresentationStore, intake: DocumentIntake, clock):
        self.presentations = presentations
        self.intake = intake
        self.clock = clock

    async def create(self, owner_id: UUID, title) -> Presentation:
        presentation = Presentation.create(title)
        await self.presentations.add(owner_id, presentation, self.clock.now())
        await self.intake.upsert(owner_id, material_row(presentation))
        return presentation