from datetime import datetime
from uuid import UUID

PIECE_CAP = 2000
TOKENS_PER_PIECE = 500
ATTEMPT_LIMIT = 3
DEADLINE_SECONDS = 300


class IndexingBudget:
    def __init__(self):
        self._attempts: dict[UUID, int] = {}
        self._started: dict[UUID, datetime] = {}
        self._inflight: set[UUID] = set()
        self._cancelled: set[UUID] = set()

    def begin(self, document_id: UUID, now: datetime) -> bool:
        if document_id in self._cancelled or document_id in self._inflight:
            return False
        if self._attempts.get(document_id, 0) >= ATTEMPT_LIMIT:
            return False
        self._inflight.add(document_id)
        self._attempts[document_id] = self._attempts.get(document_id, 0) + 1
        self._started.setdefault(document_id, now)
        return True

    def finish(self, document_id: UUID) -> None:
        self._inflight.discard(document_id)

    def attempts(self, document_id: UUID) -> int:
        return self._attempts.get(document_id, 0)

    def overdue(self, document_id: UUID, now: datetime) -> bool:
        started = self._started.get(document_id)
        if started is None:
            return False
        return (now - started).total_seconds() >= DEADLINE_SECONDS

    def cancel(self, document_id: UUID) -> None:
        self._cancelled.add(document_id)

    def cancelled(self, document_id: UUID) -> bool:
        return document_id in self._cancelled


def over_piece_cap(piece_count: int, text: str) -> bool:
    return piece_count > PIECE_CAP or len(text.split()) > PIECE_CAP * TOKENS_PER_PIECE
