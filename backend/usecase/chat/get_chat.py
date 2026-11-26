from dataclasses import replace
from uuid import UUID

from domain.chat.chat import Chat
from domain.document.document import DELETED_SOURCE_NAME
from usecase.chat.errors import ChatNotFound
from usecase.chat.ports import ChatStore, DocumentVectors
from usecase.document.errors import StoreUnavailable
from usecase.document.ports import DocumentIntake, PieceIndex


class GetChat:
    def __init__(
        self,
        chats: ChatStore,
        pieces: PieceIndex,
        vectors: DocumentVectors,
        documents: DocumentIntake | None = None,
    ):
        self.chats = chats
        self.pieces = pieces
        self.vectors = vectors
        self.documents = documents

    async def open(self, owner_id: UUID, chat_id: UUID) -> Chat:
        found = await self.chats.get(owner_id, chat_id)
        if found is None:
            raise ChatNotFound()
        found = await self._named(owner_id, found)
        if await self.vectors.ready(found.document_id):
            return found.with_vectors(True)
        try:
            await self.vectors.write(found.document_id, await self.pieces.placed(found.document_id))
        except StoreUnavailable:
            return found.with_vectors(False)
        return found.with_vectors(await self.vectors.ready(found.document_id))

    async def _named(self, owner_id: UUID, chat: Chat) -> Chat:
        if self.documents is None:
            return chat
        material = await self.documents.get(owner_id, chat.document_id)
        if material is None:
            return replace(chat, document_name=DELETED_SOURCE_NAME)
        return chat
