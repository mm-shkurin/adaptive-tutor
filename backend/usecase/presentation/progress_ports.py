from datetime import datetime
from typing import Protocol
from uuid import UUID

from domain.document.document import Document
from domain.quiz.quiz import Quiz


class OwnerMaterials(Protocol):
    async def chips(self, owner_id: UUID) -> tuple[Document, ...]: ...

    async def owned(self, owner_id: UUID, material_id: UUID) -> Document | None: ...


class OwnerActivity(Protocol):
    async def quiz_finishes(self, owner_id: UUID) -> tuple[tuple[Quiz, datetime], ...]: ...

    async def chat_person_sends(self, owner_id: UUID) -> tuple[datetime, ...]: ...