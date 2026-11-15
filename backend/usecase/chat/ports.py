from datetime import datetime
from typing import Protocol
from uuid import UUID

from domain.chat.chat import Chat
from domain.chat.source import Source
from domain.document.placed_text import PlacedPiece


class ChatStore(Protocol):
    async def add(self, owner_id: UUID, chat: Chat, created_at: datetime) -> None: ...

    async def list_for(self, owner_id: UUID) -> tuple[Chat, ...]: ...

    async def get(self, owner_id: UUID, chat_id: UUID) -> Chat | None: ...

    async def save(self, owner_id: UUID, chat: Chat) -> None: ...

    async def find_attempt(self, owner_id: UUID, chat_id: UUID, attempt_key: str): ...

    async def save_attempt(self, owner_id: UUID, chat_id: UUID, attempt_key: str, attempt) -> None: ...


class MaterialSearch(Protocol):
    async def ready(self, document_id: UUID) -> bool: ...

    async def matching(self, document_id: UUID, question: str) -> tuple[Source, ...]: ...


class DocumentVectors(Protocol):
    async def ready(self, document_id: UUID) -> bool: ...

    async def write(self, document_id: UUID, pieces: tuple[PlacedPiece, ...]) -> None: ...


class Tutor(Protocol):
    async def answer(self, model: str, mode: str, question: str, sources: tuple[Source, ...]) -> str: ...
