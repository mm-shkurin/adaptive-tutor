from dataclasses import dataclass
from uuid import UUID

from domain.chat.chat import Chat
from usecase.chat.create_chat import CreateChat
from usecase.chat.ports import ChatStore


@dataclass(frozen=True)
class OpenedChat:
    chat: Chat
    created: bool


class OpenChat:
    def __init__(self, create: CreateChat, chats: ChatStore):
        self.create = create
        self.chats = chats

    async def open(self, owner_id: UUID, document_id: UUID) -> OpenedChat:
        existing = await self.chats.newest_for_document(owner_id, document_id)
        if existing is not None:
            return OpenedChat(existing, created=False)
        return OpenedChat(await self.create.start(owner_id, document_id), created=True)
