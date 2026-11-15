from uuid import UUID

from domain.chat.source import REPLY_SOURCE_LIMIT, Source
from domain.document.placed_text import PlacedPiece
from usecase.document.errors import StoreUnavailable


class QdrantPieces:
    def __init__(self, embeddings, qdrant, pieces=None):
        self._embeddings = embeddings
        self._qdrant = qdrant
        self._pieces = pieces
        self._last_failed: dict[UUID, int] = {}

    async def write(self, document_id: UUID, pieces: tuple[PlacedPiece, ...]) -> None:
        if not pieces:
            return
        present = await self._qdrant.ordinals(document_id)
        for ordinal, piece in enumerate(pieces):
            if ordinal in present:
                continue
            try:
                vectors = await self._embeddings.embed((piece.text,))
                await self._qdrant.upsert(document_id, ((ordinal, piece),), vectors)
            except StoreUnavailable:
                self._last_failed[document_id] = ordinal
                raise

    async def ready(self, document_id: UUID) -> bool:
        expected = await self._expected(document_id)
        if expected <= 0:
            return False
        return await self._qdrant.count(document_id) == expected

    def failed_ordinal(self, document_id: UUID) -> int | None:
        return self._last_failed.get(document_id)

    async def matching(self, document_id: UUID, question: str) -> tuple[Source, ...]:
        if question.strip() == "":
            return ()
        vectors = await self._embeddings.embed((question,))
        hits = await self._qdrant.search(document_id, vectors[0], REPLY_SOURCE_LIMIT)
        return tuple(_source(hit) for hit in hits)

    async def _expected(self, document_id: UUID) -> int:
        if self._pieces is None:
            return 1 if await self._qdrant.count(document_id) > 0 else 0
        return len(await self._pieces.placed(document_id))


def _source(hit: dict) -> Source:
    payload = hit["payload"]
    page = payload.get("page")
    return Source(page if isinstance(page, int) else None, payload["text"])
