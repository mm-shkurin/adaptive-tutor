from uuid import UUID

from domain.chat.source import Source


class PreferSeededSearch:
    def __init__(self, seeded, vectors):
        self._seeded = seeded
        self._vectors = vectors

    def seed(self, document_id: UUID, pieces: tuple[Source, ...]) -> None:
        self._seeded.seed(document_id, pieces)

    async def ready(self, document_id: UUID) -> bool:
        if self._seeded.has(document_id):
            return True
        return await self._vectors.ready(document_id)

    async def matching(self, document_id: UUID, question: str) -> tuple[Source, ...]:
        if self._seeded.has(document_id):
            return await self._seeded.matching(document_id, question)
        return await self._vectors.matching(document_id, question)
