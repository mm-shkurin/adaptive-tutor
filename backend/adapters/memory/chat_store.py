from datetime import datetime
from uuid import UUID

from domain.chat.chat import Chat
from usecase.chat.errors import ChatNotFound
from usecase.chat.send_message import Attempt


class MemoryChatStore:
    def __init__(self):
        self._rows: list[tuple[UUID, Chat, datetime]] = []
        self._attempts: dict[tuple[UUID, UUID, str], Attempt] = {}

    async def add(self, owner_id: UUID, chat: Chat, created_at: datetime) -> None:
        self._rows.append((owner_id, chat, created_at))

    async def list_for(self, owner_id: UUID) -> tuple[Chat, ...]:
        owned = [row for row in self._rows if row[0] == owner_id]
        owned.sort(key=lambda row: (row[2], row[1].id), reverse=True)
        return tuple(row[1] for row in owned)

    async def get(self, owner_id: UUID, chat_id: UUID) -> Chat | None:
        for owner, chat, _created in self._rows:
            if owner == owner_id and chat.id == chat_id:
                return chat
        return None

    async def newest_for_document(self, owner_id: UUID, document_id: UUID) -> Chat | None:
        owned = [
            row
            for row in self._rows
            if row[0] == owner_id and row[1].document_id == document_id
        ]
        if not owned:
            return None
        owned.sort(key=lambda row: (row[2], row[1].id), reverse=True)
        return owned[0][1]

    async def save(self, owner_id: UUID, chat: Chat) -> None:
        for index, (owner, stored, created) in enumerate(self._rows):
            if owner == owner_id and stored.id == chat.id:
                self._rows[index] = (owner, chat, created)
                return
        raise ChatNotFound()

    async def find_attempt(self, owner_id: UUID, chat_id: UUID, attempt_key: str) -> Attempt | None:
        return self._attempts.get((owner_id, chat_id, attempt_key))

    async def save_attempt(
        self, owner_id: UUID, chat_id: UUID, attempt_key: str, attempt: Attempt
    ) -> None:
        if await self.get(owner_id, chat_id) is None:
            raise ChatNotFound()
        self._attempts[(owner_id, chat_id, attempt_key)] = attempt
