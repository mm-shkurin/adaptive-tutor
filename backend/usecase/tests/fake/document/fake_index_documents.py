from uuid import UUID

from usecase.document.index_documents import RETRY, IndexDocuments


class FakeIndexDocuments(IndexDocuments):
    def __init__(self, intake, files, reader, pieces, clock=None):
        super().__init__(intake, files, reader, pieces, clock)
        self._fail_table_after_text = False
        self._always_fail: set[UUID] = set()

    def fail_table_after_text_step(self) -> None:
        self._fail_table_after_text = True

    def fail_indexing_always(self, document_id: UUID) -> None:
        self._always_fail.add(document_id)

    async def _refusal(self, document, read) -> str | None:
        if document.id in self._always_fail:
            return RETRY
        if not self._fail_table_after_text:
            return None
        table = read.table.rstrip("\n")
        return table if table else "table"
