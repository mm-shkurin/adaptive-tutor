import asyncio
from uuid import UUID

from domain.document.placed_text import PlacedPiece
from usecase.document.errors import StoreUnavailable


class ProbePieceIndex:
    def __init__(self, probe):
        self._probe = probe
        self.stored: dict[UUID, tuple[str, ...]] = {}
        self.pages: dict[UUID, tuple[int | None, ...]] = {}
        self.slides: dict[UUID, tuple[int | None, ...]] = {}
        self.extracted_text: dict[UUID, str] = {}
        self.dead = False

    async def replace(
        self,
        document_id: UUID,
        pieces: tuple[str, ...],
        extracted: str,
        pages: tuple[int | None, ...] = (),
        slides: tuple[int | None, ...] = (),
    ) -> None:
        if self.dead:
            raise StoreUnavailable()
        delay = self._probe.search_store_call_delay_seconds()
        if delay > 0:
            await asyncio.sleep(delay)
        deadline = self._probe.external_call_deadline_seconds()
        if delay >= deadline:
            raise StoreUnavailable()
        outcome = self._probe.search_store_outcome()
        if outcome in {"refuses", "answers unreadable", "times out"}:
            raise StoreUnavailable()
        self.stored[document_id] = pieces
        self.pages[document_id] = pages
        self.slides[document_id] = slides
        self.extracted_text[document_id] = extracted
        self._probe.replace_pieces(str(document_id), pieces, extracted, pages, slides)

    async def pieces(self, document_id: UUID) -> tuple[str, ...]:
        if self.dead:
            raise StoreUnavailable()
        return self.stored.get(document_id, ())

    async def placed(self, document_id: UUID) -> tuple[PlacedPiece, ...]:
        if self.dead:
            raise StoreUnavailable()
        texts = self.stored.get(document_id, ())
        pages = self.pages.get(document_id, ())
        slides = self.slides.get(document_id, ())
        return tuple(
            PlacedPiece(
                text,
                pages[index] if index < len(pages) else None,
                slides[index] if index < len(slides) else None,
            )
            for index, text in enumerate(texts)
        )

    async def extracted(self, document_id: UUID) -> str:
        if self.dead:
            raise StoreUnavailable()
        return self.extracted_text.get(document_id, "")
