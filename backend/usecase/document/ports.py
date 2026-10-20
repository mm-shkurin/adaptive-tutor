from dataclasses import dataclass
from typing import Protocol
from uuid import UUID

from domain.document.document import Document


@dataclass(frozen=True)
class PdfRead:
    text: str
    table: str
    page_count: int


class DocumentIntake(Protocol):
    async def store(self, owner_id: UUID, document: Document, content: bytes) -> None: ...

    async def get(self, owner_id: UUID, document_id: UUID) -> Document | None: ...

    async def save(self, document: Document) -> None: ...

    async def next_waiting(self) -> tuple[Document, bytes] | None: ...


class FileStore(Protocol):
    async def put(self, document_id: UUID, content: bytes) -> None: ...

    async def get(self, document_id: UUID) -> bytes | None: ...

    async def delete(self, document_id: UUID) -> None: ...


class PdfReader(Protocol):
    async def read(self, content: bytes) -> PdfRead: ...


class PieceIndex(Protocol):
    async def replace(self, document_id: UUID, pieces: tuple[str, ...], extracted: str) -> None: ...

    async def pieces(self, document_id: UUID) -> tuple[str, ...]: ...

    async def extracted(self, document_id: UUID) -> str: ...
