from uuid import UUID

from usecase.document.errors import StoreUnavailable


class MemoryPieceIndex:
    def __init__(self, probe=None):
        self.stored: dict[UUID, tuple[str, ...]] = {}
        self.extracted_text: dict[UUID, str] = {}
        self._probe = probe
        self.dead = False

    async def replace(self, document_id: UUID, pieces: tuple[str, ...], extracted: str) -> None:
        if self.dead:
            raise StoreUnavailable()
        self.stored[document_id] = pieces
        self.extracted_text[document_id] = extracted
        if self._probe is not None:
            self._probe.replace_pieces(str(document_id), pieces, extracted)

    async def pieces(self, document_id: UUID) -> tuple[str, ...]:
        if self.dead:
            raise StoreUnavailable()
        return self.stored.get(document_id, ())

    async def extracted(self, document_id: UUID) -> str:
        if self.dead:
            raise StoreUnavailable()
        return self.extracted_text.get(document_id, "")
