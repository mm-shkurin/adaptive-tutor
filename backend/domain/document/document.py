from dataclasses import dataclass, replace
from uuid import UUID, uuid4


@dataclass(frozen=True)
class Document:
    id: UUID
    name: str
    size_bytes: int
    page_count: int | None
    piece_count: int | None
    status: str
    error: str | None

    @staticmethod
    def accepted(name: str, size_bytes: int) -> "Document":
        return Document(
            id=uuid4(),
            name=name,
            size_bytes=size_bytes,
            page_count=None,
            piece_count=None,
            status="waiting",
            error=None,
        )

    def indexing(self) -> "Document":
        return replace(self, status="indexing")

    def ready(self, page_count: int, piece_count: int) -> "Document":
        return replace(self, status="ready", page_count=page_count, piece_count=piece_count, error=None)
