from uuid import UUID

from domain.chat.chat import Chat
from usecase.chat.errors import ChatNotFound
from usecase.chat.ports import ChatStore, DocumentVectors
from usecase.document.errors import StoreUnavailable
from usecase.document.ports import PieceIndex


class GetChat:
    def __init__(self, chats: ChatStore, pieces: PieceIndex, vectors: DocumentVectors):
        self.chats = chats
        self.pieces = pieces
        self.vectors = vectors

    async def open(self, owner_id: UUID, chat_id: UUID) -> Chat:
        found = await self.chats.get(owner_id, chat_id)
        if found is None:
            raise ChatNotFound()
        if await self.vectors.ready(found.document_id):
            return found.with_vectors(True)
        try:
            await self.vectors.write(found.document_id, await self.pieces.placed(found.document_id))
        except StoreUnavailable:
            return found.with_vectors(False)
        return found.with_vectors(await self.vectors.ready(found.document_id))
