from usecase.document.index_documents import IndexDocuments


class FakeIndexDocuments(IndexDocuments):
    def __init__(self, intake, files, reader, pieces, clock=None):
        super().__init__(intake, files, reader, pieces, clock)
        self._fail_table_after_text = False

    def fail_table_after_text_step(self) -> None:
        self._fail_table_after_text = True

    async def _refusal(self, document, read) -> str | None:
        if not self._fail_table_after_text:
            return None
        table = read.table.rstrip("\n")
        return table if table else "table"
