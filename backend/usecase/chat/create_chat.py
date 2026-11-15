from uuid import UUID

from domain.chat.chat import Chat
from domain.document.document import Document
from usecase.chat.errors import ChatNotFound, NoReadyDocument
from usecase.chat.ports import ChatStore
from usecase.document.ports import DocumentIntake


class CreateChat:
    def __init__(self, documents: DocumentIntake, chats: ChatStore, clock):
        self.documents = documents
        self.chats = chats
        self.clock = clock

    async def start(self, owner_id: UUID, document_id: UUID | None) -> Chat:
        chat = Chat.bound_to(await self._document(owner_id, document_id))
        await self.chats.add(owner_id, chat, self.clock.now())
        return chat

    async def _document(self, owner_id: UUID, document_id: UUID | None) -> Document:
        if document_id is None:
            return await self._newest_ready(owner_id)
        found = await self.documents.get(owner_id, document_id)
        if found is None:
            raise ChatNotFound()
        return found

    async def _newest_ready(self, owner_id: UUID) -> Document:
        page, _ = await self.documents.list_page(owner_id, 1, None)
        for document in page:
            if document.is_ready():
                return document
        raise NoReadyDocument()
