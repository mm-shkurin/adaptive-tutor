from domain.document.extracted_text import ExtractedText
from usecase.document.index_documents import IndexDocuments


class ProbeIndexDocuments(IndexDocuments):
    def __init__(self, intake, files, reader, pieces, probe):
        super().__init__(intake, files, reader, pieces)
        self._probe = probe

    async def _index(self, document, content):
        indexing = document.indexing()
        await self.intake.save(indexing)
        read = await self.reader.read(content)
        extracted = ExtractedText.compose(read.text)
        parts = extracted.pieces()
        await self.pieces.replace(document.id, parts, extracted.value)
        if self._probe.consume_fail_ready_after_pieces():
            return
        await self.intake.save(indexing.ready(read.page_count, len(parts)))
        await self.files.delete(document.id)
