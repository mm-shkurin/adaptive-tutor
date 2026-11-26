from dataclasses import replace

from domain.document.document import Document
from domain.presentation.presentation import Presentation


def material_row(presentation: Presentation, size_bytes: int = 0) -> Document:
    row = Document.presentation_row(
        presentation.id,
        presentation.title,
        presentation.status,
        presentation.piece_count,
        size_bytes,
    )
    if presentation.error:
        return replace(row, error=presentation.error)
    return row
