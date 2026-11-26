from dataclasses import replace
from uuid import UUID

from domain.chat.chat import Chat
from domain.document.document import DELETED_SOURCE_NAME
from usecase.chat.ports import ChatStore
from usecase.document.ports import DocumentIntake


class ListChats:
    def __init__(self, chats: ChatStore, documents: DocumentIntake | None = None):
        self.chats = chats
        self.documents = documents

    async def list(self, owner_id: UUID) -> tuple[Chat, ...]:
        items = await self.chats.list_for(owner_id)
        if self.documents is None:
            return items
        return tuple([await self._named(owner_id, chat) for chat in items])

    async def _named(self, owner_id: UUID, chat: Chat) -> Chat:
        found = await self.documents.get(owner_id, chat.document_id)
        if found is None:
            return replace(chat, document_name=DELETED_SOURCE_NAME)
        return chat
