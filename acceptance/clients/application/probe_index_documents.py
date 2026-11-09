from usecase.document.index_documents import PAUSE, RETRY, IndexDocuments, RetryIndex


class ProbeIndexDocuments(IndexDocuments):
    def __init__(self, intake, files, reader, pieces, probe, clock=None):
        super().__init__(intake, files, reader, pieces, clock)
        self._probe = probe
        self._failed_once: set[str] = set()

    def _note_attempt(self, document) -> None:
        self._probe.record_indexing_attempt(str(document.id))

    async def _refusal(self, document, read) -> str | None:
        document_id = str(document.id)
        outcome = self._probe.embedding_outcome()
        if outcome == "server_error":
            self._probe.record_embedding_attempt(document_id)
            return PAUSE
        if outcome in {"refuses", "unreadable"}:
            self._probe.record_embedding_attempt(document_id)
            return "embedding refused"
        if self._probe.indexing_always_fails(document_id):
            return RETRY
        if self._probe.should_fail_table_after_text():
            return self._table_failure(document_id, document.name, read)
        return None

    def _table_failure(self, document_id: str, name: str, read) -> str:
        table = read.table.rstrip("\n")
        if table:
            return table
        self._probe.remember_extracted(document_id, read.text)
        markup = _markup(name)
        if markup:
            return f"{markup}\n|Topic|Mark|\n|---|---|\n|Limits|91|"
        return "table"

    async def _store(self, document, parts, extracted) -> None:
        document_id = str(document.id)
        if self._probe.search_store_should_fail_once() and document_id not in self._failed_once:
            self._failed_once.add(document_id)
            raise RetryIndex()
        await super()._store(document, parts, extracted)

    async def _hold_ready(self, document) -> bool:
        return self._probe.consume_fail_ready_after_pieces()


def _markup(name: str) -> str:
    start = name.find("' OR 1=1")
    end = name.find(">", start)
    if start < 0 or end < 0:
        return ""
    return name[start : end + 1]
