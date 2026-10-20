from uuid import UUID


class FakePieceIndex:
    def __init__(self):
        self.stored: dict[UUID, tuple[str, ...]] = {}
        self.extracted_text: dict[UUID, str] = {}

    async def replace(self, document_id: UUID, pieces: tuple[str, ...], extracted: str) -> None:
        self.stored[document_id] = pieces
        self.extracted_text[document_id] = extracted

    async def pieces(self, document_id: UUID) -> tuple[str, ...]:
        return self.stored.get(document_id, ())

    async def extracted(self, document_id: UUID) -> str:
        return self.extracted_text.get(document_id, "")
