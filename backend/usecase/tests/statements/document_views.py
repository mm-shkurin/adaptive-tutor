from uuid import UUID

from domain.document.document import Document

PAGE_COUNT = 1
PIECE_COUNT = 2
NEIGHBOUR_PIECE_COUNT = 1


def waiting(document_id: UUID, name: str, size_bytes: int) -> Document:
    return document(document_id, name, size_bytes, None, None, "waiting")


def ready(document_id: UUID, name: str, size_bytes: int) -> Document:
    return document(document_id, name, size_bytes, PAGE_COUNT, PIECE_COUNT, "ready")


def neighbour_ready(document_id: UUID, name: str, size_bytes: int) -> Document:
    return document(document_id, name, size_bytes, PAGE_COUNT, NEIGHBOUR_PIECE_COUNT, "ready")


def failed(document_id: UUID, name: str, size_bytes: int, reason: str) -> Document:
    return document(document_id, name, size_bytes, None, None, "failed", reason)


def document(
    document_id: UUID,
    name: str,
    size_bytes: int,
    page_count: int | None,
    piece_count: int | None,
    status: str,
    error: str | None = None,
) -> Document:
    return Document(
        id=document_id,
        name=name,
        size_bytes=size_bytes,
        page_count=page_count,
        piece_count=piece_count,
        status=status,
        error=error,
    )
