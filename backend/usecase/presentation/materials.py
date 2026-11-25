from domain.document.document import Document
from domain.presentation.presentation import Presentation


def material_row(presentation: Presentation, size_bytes: int = 0) -> Document:
    return Document.presentation_row(
        presentation.id,
        presentation.title,
        presentation.status,
        presentation.piece_count,
        size_bytes,
    )