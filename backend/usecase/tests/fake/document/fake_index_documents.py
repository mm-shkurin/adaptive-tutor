import time
from uuid import UUID

from usecase.document.index_documents import PAUSE, RETRY, IndexDocuments, RetryIndex


class FakeIndexDocuments(IndexDocuments):
    def __init__(self, intake, files, reader, pieces, clock=None):
        super().__init__(intake, files, reader, pieces, clock)
        self._fail_table_after_text = False
        self._fail_ready_after_pieces_once = False
        self._always_fail: set[UUID] = set()
        self._embedding_outcome: str | None = None
        self._embedding_attempts: dict[UUID, int] = {}
        self._search_store_fail_once = False
        self._failed_once: set[UUID] = set()
        self._indexing_attempts: dict[UUID, int] = {}
        self._indexing_attempt_times: dict[UUID, list[float]] = {}
        self._remembered_extracted: dict[UUID, str] = {}

    def fail_table_after_text_step(self) -> None:
        self._fail_table_after_text = True

    def remembered_extracted(self, document_id: UUID) -> str:
        return self._remembered_extracted.get(document_id, "")

    def fail_ready_save_after_pieces_once(self) -> None:
        self._fail_ready_after_pieces_once = True

    def fail_indexing_always(self, document_id: UUID) -> None:
        self._always_fail.add(document_id)

    def set_embedding_outcome(self, outcome: str | None) -> None:
        self._embedding_outcome = outcome

    def embedding_attempts(self, document_id: UUID) -> int:
        return self._embedding_attempts.get(document_id, 0)

    def arm_search_store_fails_once_for_all(self) -> None:
        self._search_store_fail_once = True
        self._failed_once.clear()

    def indexing_attempts(self, document_id: UUID) -> int:
        return self._indexing_attempts.get(document_id, 0)

    def indexing_attempt_times(self, document_id: UUID) -> tuple[float, ...]:
        return tuple(self._indexing_attempt_times.get(document_id, ()))

    def _note_attempt(self, document) -> None:
        self._indexing_attempts[document.id] = self._indexing_attempts.get(document.id, 0) + 1
        self._indexing_attempt_times.setdefault(document.id, []).append(time.monotonic())

    async def _refusal(self, document, read) -> str | None:
        if self._embedding_outcome == "server_error":
            self._embedding_attempts[document.id] = self._embedding_attempts.get(document.id, 0) + 1
            return PAUSE
        if self._embedding_outcome in {"refuses", "unreadable"}:
            self._embedding_attempts[document.id] = self._embedding_attempts.get(document.id, 0) + 1
            return "embedding refused"
        if document.id in self._always_fail:
            return RETRY
        if not self._fail_table_after_text:
            return None
        return self._table_failure(document, read)

    def _table_failure(self, document, read) -> str:
        table = read.table.rstrip("\n")
        if table:
            return table
        self._remembered_extracted[document.id] = read.text
        markup = _markup(document.name)
        if markup:
            return f"{markup}\n|Topic|Mark|\n|---|---|\n|Limits|91|"
        return "table"

    async def _store(self, document, parts, extracted) -> None:
        if self._search_store_fail_once and document.id not in self._failed_once:
            self._failed_once.add(document.id)
            raise RetryIndex()
        await super()._store(document, parts, extracted)

    async def _hold_ready(self, document) -> bool:
        if not self._fail_ready_after_pieces_once:
            return False
        self._fail_ready_after_pieces_once = False
        return True


def _markup(name: str) -> str:
    start = name.find("' OR 1=1")
    end = name.find(">", start)
    if start < 0 or end < 0:
        return ""
    return name[start : end + 1]
