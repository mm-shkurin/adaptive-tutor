from uuid import UUID

from usecase.document.errors import StoreUnavailable


class FakePieceIndex:
    def __init__(self):
        self.stored: dict[UUID, tuple[str, ...]] = {}
        self.extracted_text: dict[UUID, str] = {}
        self._replace_counts: dict[UUID, int] = {}
        self.outcome: str | None = None

    def set_outcome(self, outcome: str | None) -> None:
        self.outcome = outcome

    async def replace(self, document_id: UUID, pieces: tuple[str, ...], extracted: str) -> None:
        if self.outcome in {"times out", "refuses", "answers unreadable"}:
            raise StoreUnavailable()
        self._replace_counts[document_id] = self._replace_counts.get(document_id, 0) + 1
        self.stored[document_id] = pieces
        self.extracted_text[document_id] = extracted

    def replace_count(self, document_id: UUID) -> int:
        return self._replace_counts.get(document_id, 0)

    async def pieces(self, document_id: UUID) -> tuple[str, ...]:
        return self.stored.get(document_id, ())

    async def extracted(self, document_id: UUID) -> str:
        return self.extracted_text.get(document_id, "")
