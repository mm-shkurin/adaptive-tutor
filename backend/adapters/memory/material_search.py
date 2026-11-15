from uuid import UUID

from domain.chat.source import Source


class MemoryMaterialSearch:
    def __init__(self):
        self._pieces: dict[UUID, tuple[Source, ...]] = {}
        self._ready: set[UUID] = set()

    def seed(self, document_id: UUID, pieces: tuple[Source, ...]) -> None:
        self._pieces[document_id] = pieces
        self._ready.add(document_id)

    def has(self, document_id: UUID) -> bool:
        return document_id in self._ready

    async def ready(self, document_id: UUID) -> bool:
        return document_id in self._ready

    async def matching(self, document_id: UUID, question: str) -> tuple[Source, ...]:
        if question.strip() == "":
            return ()
        return self._pieces.get(document_id, ())
