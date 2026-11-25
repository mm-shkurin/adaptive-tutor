from dataclasses import dataclass, replace
from uuid import UUID, uuid4

from domain.presentation.errors import (
    InvalidSlideOrder,
    NoSlides,
    SlideLimit,
    TitleTooLong,
    TooManySlides,
    UnknownSlide,
)
from domain.presentation.parsed_office import ParsedOfficeSlide
from domain.presentation.slide import Slide

_DEFAULT_TITLE = "Новая презентация"
_MAX_TITLE = 80
_MAX_SLIDES = 40


@dataclass(frozen=True)
class Presentation:
    id: UUID
    title: str
    status: str
    slides: tuple[Slide, ...]
    piece_count: int | None
    error: str

    @staticmethod
    def create(title: object = None) -> "Presentation":
        return Presentation(
            id=uuid4(),
            title=_canonical_title(title),
            status="draft",
            slides=(),
            piece_count=None,
            error="",
        )

    def add_image(self, content: bytes) -> tuple["Presentation", Slide]:
        self._ensure_room(1)
        slide = Slide.image(len(self.slides) + 1)
        updated = replace(self, slides=self.slides + (slide,))
        return updated, slide

    def add_pdf_pages(self, pdf_document_id: UUID, pages: tuple[int, ...]) -> "Presentation":
        self._ensure_room(len(pages))
        updated = self
        for page in pages:
            slide = Slide.pdf_page(len(updated.slides) + 1, pdf_document_id, page)
            updated = replace(updated, slides=updated.slides + (slide,))
        return updated

    def add_office_slides(
        self, source: str, parsed: tuple[ParsedOfficeSlide, ...]
    ) -> tuple["Presentation", tuple[Slide, ...]]:
        self._ensure_room(len(parsed))
        updated = self
        added: list[Slide] = []
        for item in parsed:
            slide = Slide.office(len(updated.slides) + 1, source, item.text)
            updated = replace(updated, slides=updated.slides + (slide,))
            added.append(slide)
        return updated, tuple(added)

    def remove_slide(self, slide_id: UUID) -> "Presentation":
        kept = tuple(slide for slide in self.slides if slide.id != slide_id)
        return replace(self, slides=_reseat(kept))

    def reorder(self, slide_ids: tuple[UUID, ...]) -> "Presentation":
        if len(slide_ids) != len(self.slides):
            raise InvalidSlideOrder()
        by_id = {slide.id: slide for slide in self.slides}
        if set(slide_ids) != set(by_id):
            raise InvalidSlideOrder()
        ordered = tuple(by_id[slide_id] for slide_id in slide_ids)
        return replace(self, slides=_reseat(ordered))

    def patch_text(self, slide_id: UUID, text: str) -> "Presentation":
        return self._map_slide(slide_id, lambda slide: slide.with_text(text))

    def require_indexable(self) -> None:
        count = len(self.slides)
        if count == 0:
            raise NoSlides()
        if count > _MAX_SLIDES:
            raise TooManySlides()

    def begin_index(self) -> "Presentation":
        self.require_indexable()
        return replace(self, status="indexing", error="")

    def ready(self, slides: tuple[Slide, ...], piece_count: int) -> "Presentation":
        return replace(self, status="ready", slides=slides, piece_count=piece_count, error="")

    def failed(self, reason: str) -> "Presentation":
        return replace(self, status="failed", error=reason)

    def rename(self, title: object) -> "Presentation":
        return replace(self, title=_canonical_title(title))

    def slide_count(self) -> int:
        return len(self.slides)

    def json(self) -> dict:
        return {
            "id": str(self.id),
            "title": self.title,
            "status": self.status,
            "slide_count": len(self.slides),
            "piece_count": self.piece_count,
            "error": self.error or None,
            "slides": [slide.json() for slide in self.slides],
        }

    def _ensure_room(self, adding: int) -> None:
        if len(self.slides) + adding > _MAX_SLIDES:
            raise SlideLimit()

    def _map_slide(self, slide_id: UUID, change) -> "Presentation":
        updated: list[Slide] = []
        found = False
        for slide in self.slides:
            if slide.id == slide_id:
                updated.append(change(slide))
                found = True
            else:
                updated.append(slide)
        if not found:
            raise UnknownSlide()
        return replace(self, slides=tuple(updated))


def _canonical_title(raw: object) -> str:
    text = _DEFAULT_TITLE if raw is None else str(raw).strip()
    if text == "":
        text = _DEFAULT_TITLE
    if len(text) > _MAX_TITLE:
        raise TitleTooLong()
    return text


def _reseat(slides: tuple[Slide, ...]) -> tuple[Slide, ...]:
    return tuple(slide.with_position(index + 1) for index, slide in enumerate(slides))