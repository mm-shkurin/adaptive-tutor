from datetime import datetime
from uuid import UUID

from domain.chat.chat import Chat


class MemoryChatStore:
    def __init__(self):
        self._rows: list[tuple[UUID, Chat, datetime]] = []

    async def add(self, owner_id: UUID, chat: Chat, created_at: datetime) -> None:
        self._rows.append((owner_id, chat, created_at))

    async def list_for(self, owner_id: UUID) -> tuple[Chat, ...]:
        owned = [row for row in self._rows if row[0] == owner_id]
        owned.sort(key=lambda row: (row[2], row[1].id), reverse=True)
        return tuple(row[1] for row in owned)
