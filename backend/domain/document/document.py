from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class Document:
    id: UUID
    name: str
    size_bytes: int
    page_count: int | None
    piece_count: int | None
    status: str
    error: str | None
