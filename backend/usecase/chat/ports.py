from datetime import datetime
from typing import Protocol
from uuid import UUID

from domain.chat.chat import Chat


class ChatStore(Protocol):
    async def add(self, owner_id: UUID, chat: Chat, created_at: datetime) -> None: ...

    async def list_for(self, owner_id: UUID) -> tuple[Chat, ...]: ...
