from uuid import UUID

from domain.chat.chat import Chat
from usecase.chat.ports import ChatStore


class ListChats:
    def __init__(self, chats: ChatStore):
        self.chats = chats

    async def list(self, owner_id: UUID) -> tuple[Chat, ...]:
        return await self.chats.list_for(owner_id)
