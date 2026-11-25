from datetime import datetime
from uuid import UUID

from adapters.persistence.tables_presentations import PresentationRow, PresentationSlideRow
from domain.presentation.presentation import Presentation
from domain.presentation.slide import Slide


def new_row(owner_id: UUID, presentation: Presentation, created_at: datetime) -> PresentationRow:
    row = PresentationRow(
        id=presentation.id,
        owner_id=owner_id,
        title=presentation.title,
        status=presentation.status,
        piece_count=presentation.piece_count,
        error=presentation.error or None,
        created_at=created_at,
        slides=[_slide_row(presentation.id, slide) for slide in presentation.slides],
    )
    return row


def apply_state(row: PresentationRow, presentation: Presentation) -> None:
    row.title = presentation.title
    row.status = presentation.status
    row.piece_count = presentation.piece_count
    row.error = presentation.error or None
    row.slides.clear()
    row.slides.extend(_slide_row(presentation.id, slide) for slide in presentation.slides)


def presentation_from_row(row: PresentationRow) -> Presentation:
    return Presentation(
        id=row.id,
        title=row.title,
        status=row.status,
        slides=tuple(_slide(item) for item in row.slides),
        piece_count=row.piece_count,
        error=row.error or "",
    )


def presentation_from_json(data: dict) -> Presentation:
    return Presentation(
        id=UUID(data["id"]),
        title=data["title"],
        status=data["status"],
        slides=tuple(_slide_json(item) for item in data["slides"]),
        piece_count=data.get("piece_count"),
        error=data.get("error") or "",
    )


def _slide_row(presentation_id: UUID, slide: Slide) -> PresentationSlideRow:
    return PresentationSlideRow(
        id=slide.id,
        presentation_id=presentation_id,
        position=slide.position,
        source=slide.source,
        text=slide.text,
        formula_phrase=slide.formula_phrase or None,
        formula_latex=slide.formula_latex or None,
        empty=slide.empty,
        pdf_document_id=slide.pdf_document_id,
        pdf_page=slide.pdf_page,
    )


def _slide(row: PresentationSlideRow) -> Slide:
    return Slide(
        id=row.id,
        position=row.position,
        source=row.source,
        text=row.text,
        formula_phrase=row.formula_phrase or "",
        formula_latex=row.formula_latex or "",
        empty=row.empty,
        pdf_document_id=row.pdf_document_id,
        pdf_page=row.pdf_page,
    )


def _slide_json(item: dict) -> Slide:
    pdf_id = item.get("pdf_document_id")
    return Slide(
        id=UUID(item["id"]),
        position=item["position"],
        source=item["source"],
        text=item["text"],
        formula_phrase=item.get("formula_phrase") or "",
        formula_latex=item.get("formula_latex") or "",
        empty=item["empty"],
        pdf_document_id=UUID(pdf_id) if pdf_id else None,
        pdf_page=item.get("pdf_page"),
    )