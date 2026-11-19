from uuid import UUID

from domain.chat.source import Source
from usecase.chat.errors import ReplyFailed


class MemoryMaterialSearch:
    def __init__(self):
        self._pieces: dict[UUID, tuple[Source, ...]] = {}
        self._ready: set[UUID] = set()
        self._fail = False

    def seed(self, document_id: UUID, pieces: tuple[Source, ...]) -> None:
        self._pieces[document_id] = pieces
        self._ready.add(document_id)

    def has(self, document_id: UUID) -> bool:
        return document_id in self._ready

    def fail(self) -> None:
        self._fail = True

    def clear_fail(self) -> None:
        self._fail = False

    async def ready(self, document_id: UUID) -> bool:
        return document_id in self._ready

    async def matching(self, document_id: UUID, question: str) -> tuple[Source, ...]:
        if self._fail:
            raise ReplyFailed()
        if question.strip() == "":
            return ()
        return self._pieces.get(document_id, ())
