from domain.document.document import Document
from domain.document.extracted_text import ExtractedText
from usecase.document.ports import DocumentIntake, FileStore, PdfReader, PieceIndex


class IndexDocuments:
    def __init__(self, intake: DocumentIntake, files: FileStore, reader: PdfReader, pieces: PieceIndex):
        self.intake = intake
        self.files = files
        self.reader = reader
        self.pieces = pieces

    async def index_waiting(self) -> None:
        claimed = await self.intake.next_waiting()
        if claimed is None:
            return
        await self._index(claimed[0], claimed[1])

    async def _index(self, document: Document, content: bytes) -> None:
        indexing = document.indexing()
        await self.intake.save(indexing)
        read = await self.reader.read(content)
        extracted = ExtractedText.compose(read.text)
        parts = extracted.pieces()
        await self.pieces.replace(document.id, parts, extracted.value)
        await self.intake.save(indexing.ready(read.page_count, len(parts)))
        await self.files.delete(document.id)
