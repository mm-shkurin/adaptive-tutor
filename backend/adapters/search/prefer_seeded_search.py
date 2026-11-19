from datetime import timedelta
from uuid import UUID

from domain.chat.source import Source


class PreferSeededSearch:
    def __init__(self, seeded, vectors, clock=None):
        self._seeded = seeded
        self._vectors = vectors
        self._clock = clock
        self._advance_ms = None

    def seed(self, document_id: UUID, pieces: tuple[Source, ...]) -> None:
        self._seeded.seed(document_id, pieces)

    def advance_clock_on_match(self, offset_ms: int | None) -> None:
        self._advance_ms = offset_ms

    def fail(self) -> None:
        self._seeded.fail()

    def clear_fail(self) -> None:
        self._seeded.clear_fail()

    async def ready(self, document_id: UUID) -> bool:
        if self._seeded.has(document_id):
            return True
        return await self._vectors.ready(document_id)

    async def matching(self, document_id: UUID, question: str) -> tuple[Source, ...]:
        if self._seeded.has(document_id):
            found = await self._seeded.matching(document_id, question)
        else:
            found = await self._vectors.matching(document_id, question)
        if self._clock is not None and self._advance_ms is not None:
            self._clock.moment += timedelta(milliseconds=self._advance_ms)
            self._advance_ms = None
        return found
