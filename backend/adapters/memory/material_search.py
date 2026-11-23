from uuid import UUID

from domain.chat.source import Source
from usecase.chat.errors import ReplyFailed


class MemoryMaterialSearch:
    def __init__(self):
        self._pieces: dict[UUID, tuple[Source, ...]] = {}
        self._ready: set[UUID] = set()
        self._fail = False
        self._error = None
        self.live = 0

    def seed(self, document_id: UUID, pieces: tuple[Source, ...]) -> None:
        self._pieces[document_id] = pieces
        self._ready.add(document_id)

    def has(self, document_id: UUID) -> bool:
        return document_id in self._ready

    def fail(self, error=None) -> None:
        self._fail = True
        self._error = error

    def clear_fail(self) -> None:
        self._fail = False
        self._error = None

    async def ready(self, document_id: UUID) -> bool:
        async def action():
            return document_id in self._ready

        return await self._guard(action)

    async def matching(self, document_id: UUID, question: str) -> tuple[Source, ...]:
        async def action():
            if self._fail:
                raise self._error if self._error is not None else ReplyFailed()
            if question.strip() == "":
                return ()
            return self._pieces.get(document_id, ())

        return await self._guard(action)

    async def _guard(self, action):
        self.live += 1
        try:
            return await action()
        finally:
            self.live -= 1
