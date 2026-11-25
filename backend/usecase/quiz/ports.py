from datetime import datetime
from typing import Protocol
from uuid import UUID

from domain.chat.source import Source
from domain.quiz.quiz import Quiz

LIST_CAP = 100


class QuizStore(Protocol):
    async def find_by_key(self, owner_id: UUID, key: str) -> Quiz | None: ...

    async def add(self, owner_id: UUID, quiz: Quiz, created_at: datetime, key: str) -> None: ...

    async def with_key(self, owner_id: UUID, key: str, build): ...

    async def list_for(self, owner_id: UUID) -> tuple[Quiz, ...]: ...

    async def get(self, owner_id: UUID, quiz_id: UUID) -> Quiz | None: ...

    async def update(self, owner_id: UUID, quiz_id: UUID, change) -> Quiz: ...

    async def delete_owned(self, owner_id: UUID) -> None: ...

    async def finishes_for(self, owner_id: UUID) -> tuple[tuple[Quiz, datetime], ...]: ...


class QuizTutor(Protocol):
    async def compose(self, model: str, topic: str, count: int, pieces: tuple[Source, ...]) -> object: ...


class MaterialSearch(Protocol):
    async def matching(self, document_id: UUID, question: str) -> tuple[Source, ...]: ...
