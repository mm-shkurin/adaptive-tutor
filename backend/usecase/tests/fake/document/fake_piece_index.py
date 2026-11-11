from uuid import UUID

from usecase.document.errors import StoreUnavailable

_EXTERNAL_CALL_DEADLINE_SECONDS = 0.12


class FakePieceIndex:
    def __init__(self):
        self.stored: dict[UUID, tuple[str, ...]] = {}
        self.extracted_text: dict[UUID, str] = {}
        self._replace_counts: dict[UUID, int] = {}
        self.outcome: str | None = None
        self._call_delay: float | None = None
        self._deadline = _EXTERNAL_CALL_DEADLINE_SECONDS

    def set_outcome(self, outcome: str | None) -> None:
        self.outcome = outcome

    def prepare_call(self) -> None:
        self._call_delay = None
        self.outcome = None

    def finish_just_before_deadline(self) -> None:
        self._call_delay = self._deadline - 0.02
        self.outcome = None

    def reach_deadline(self) -> None:
        self._call_delay = self._deadline + 0.02
        self.outcome = "times out"

    async def replace(self, document_id: UUID, pieces: tuple[str, ...], extracted: str) -> None:
        delay = 0.0 if self._call_delay is None else self._call_delay
        if delay >= self._deadline:
            raise StoreUnavailable()
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
