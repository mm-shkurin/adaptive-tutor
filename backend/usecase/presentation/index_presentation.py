from uuid import UUID

from domain.document.extracted_text import ExtractedText
from domain.presentation.presentation import Presentation
from domain.presentation.slide import Slide
from usecase.document.ports import DocumentIntake, PieceIndex
from usecase.presentation.errors import PresentationNotFound
from usecase.presentation.materials import material_row
from usecase.presentation.ports import Ocr, PresentationStore


class IndexPresentation:
    def __init__(
        self,
        presentations: PresentationStore,
        intake: DocumentIntake,
        pieces: PieceIndex,
        ocr: Ocr,
    ):
        self.presentations = presentations
        self.intake = intake
        self.pieces = pieces
        self.ocr = ocr

    async def index(self, owner_id: UUID, presentation_id: UUID, key: str) -> tuple[Presentation, bool]:
        async def build() -> Presentation:
            current = await self._owned(owner_id, presentation_id)
            if current.status == "ready":
                return current
            working = current.begin_index()
            await self.presentations.save(owner_id, working)
            await self.intake.upsert(owner_id, material_row(working))
            indexed_slides: list[Slide] = []
            searchable: list[str] = []
            pages: list[int | None] = []
            slides: list[int] = []
            for slide in working.slides:
                content = await self.presentations.take_bytes(owner_id, presentation_id, slide.id)
                text = ""
                if content is not None:
                    text = await self.ocr.read(slide.id, content)
                indexed = slide.mark_indexed(text)
                indexed_slides.append(indexed)
                if not indexed.empty and text.strip():
                    searchable.append(text.strip())
                    pages.append(indexed.pdf_page)
                    slides.append(indexed.position)
            ready = working.ready(tuple(indexed_slides), len(searchable))
            extracted = ExtractedText.compose("\n\n".join(searchable)).value
            await self.pieces.replace(
                presentation_id, tuple(searchable), extracted, tuple(pages), tuple(slides)
            )
            await self.presentations.clear_bytes(owner_id, presentation_id)
            await self.presentations.save(owner_id, ready)
            await self.intake.upsert(owner_id, material_row(ready))
            return ready

        return await self.presentations.with_index_key(owner_id, presentation_id, key, build)

    async def _owned(self, owner_id: UUID, presentation_id: UUID) -> Presentation:
        found = await self.presentations.get(owner_id, presentation_id)
        if found is None:
            raise PresentationNotFound()
        if found.status not in {"draft", "ready", "indexing"}:
            raise PresentationNotFound()
        return found