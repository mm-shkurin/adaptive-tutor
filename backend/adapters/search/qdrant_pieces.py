from uuid import UUID

from domain.chat.source import REPLY_SOURCE_LIMIT, Source
from domain.document.placed_text import PlacedPiece


class QdrantPieces:
    def __init__(self, embeddings, qdrant):
        self._embeddings = embeddings
        self._qdrant = qdrant

    async def write(self, document_id: UUID, pieces: tuple[PlacedPiece, ...]) -> None:
        if not pieces:
            return
        vectors = await self._embeddings.embed(tuple(piece.text for piece in pieces))
        await self._qdrant.upsert(document_id, pieces, vectors)

    async def ready(self, document_id: UUID) -> bool:
        return await self._qdrant.count(document_id) > 0

    async def matching(self, document_id: UUID, question: str) -> tuple[Source, ...]:
        if question.strip() == "":
            return ()
        vectors = await self._embeddings.embed((question,))
        hits = await self._qdrant.search(document_id, vectors[0], REPLY_SOURCE_LIMIT)
        return tuple(_source(hit) for hit in hits)


def _source(hit: dict) -> Source:
    payload = hit["payload"]
    page = payload.get("page")
    return Source(page if isinstance(page, int) else None, payload["text"])
