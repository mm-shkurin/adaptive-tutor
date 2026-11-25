from uuid import UUID

from domain.presentation.errors import UnknownSlide
from domain.presentation.presentation import Presentation
from usecase.document.ports import DocumentIntake
from usecase.presentation.errors import PresentationNotFound
from usecase.presentation.materials import material_row
from usecase.presentation.ports import PresentationStore


class PatchPresentation:
    def __init__(self, presentations: PresentationStore, intake: DocumentIntake):
        self.presentations = presentations
        self.intake = intake

    async def patch(self, owner_id: UUID, presentation_id: UUID, body: dict) -> Presentation:
        current = await self._owned(owner_id, presentation_id)
        updated = self._apply(current, body)
        await self.presentations.save(owner_id, updated)
        await self.intake.upsert(owner_id, material_row(updated))
        return updated

    async def delete_slide(self, owner_id: UUID, presentation_id: UUID, slide_id: UUID) -> Presentation:
        current = await self._owned(owner_id, presentation_id)
        if not any(slide.id == slide_id for slide in current.slides):
            raise PresentationNotFound()
        updated = current.remove_slide(slide_id)
        await self.presentations.save(owner_id, updated)
        await self.intake.upsert(owner_id, material_row(updated))
        return updated

    async def _owned(self, owner_id: UUID, presentation_id: UUID) -> Presentation:
        found = await self.presentations.get(owner_id, presentation_id)
        if found is None:
            raise PresentationNotFound()
        return found

    def _apply(self, current: Presentation, body: dict) -> Presentation:
        updated = current
        if "title" in body and body["title"] is not None:
            updated = updated.rename(body["title"])
        order = body.get("slide_order")
        if order:
            updated = updated.reorder(tuple(UUID(str(slide_id)) for slide_id in order))
        for row in body.get("slides") or []:
            slide_id = UUID(str(row["id"]))
            if current.status != "ready":
                raise UnknownSlide()
            updated = updated.patch_text(slide_id, str(row.get("text", "")))
        return updated