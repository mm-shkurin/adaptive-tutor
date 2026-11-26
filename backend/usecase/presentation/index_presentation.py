from uuid import UUID

from domain.document.extracted_text import ExtractedText
from domain.presentation.presentation import Presentation
from domain.presentation.slide import Slide
from domain.presentation.weak_ocr import is_weak_ocr
from usecase.document.errors import StoreUnavailable
from usecase.document.ports import DocumentIntake, FileStore, PdfRead, PdfReader, PieceIndex
from usecase.presentation.errors import OcrUnavailable, PresentationNotFound
from usecase.presentation.materials import material_row
from usecase.presentation.ports import FormulaAssist, Ocr, PresentationStore


class IndexPresentation:
    def __init__(
        self,
        presentations: PresentationStore,
        intake: DocumentIntake,
        pieces: PieceIndex,
        ocr: Ocr,
        files: FileStore,
        reader: PdfReader,
        formulas: FormulaAssist,
    ):
        self.presentations = presentations
        self.intake = intake
        self.pieces = pieces
        self.ocr = ocr
        self.files = files
        self.reader = reader
        self.formulas = formulas

    async def index(self, owner_id: UUID, presentation_id: UUID, key: str) -> tuple[Presentation, bool]:
        async def build() -> Presentation:
            current = await self._owned(owner_id, presentation_id)
            if current.status == "ready":
                return current
            working = current.begin_index()
            await self.presentations.save(owner_id, working)
            await self.intake.upsert(owner_id, material_row(working))
            try:
                return await self._finish(owner_id, presentation_id, working)
            except OcrUnavailable:
                return await self._fail(owner_id, working, "ocr refused")
            except StoreUnavailable:
                return await self._fail(owner_id, working, "search store refused")

        return await self.presentations.with_index_key(owner_id, presentation_id, key, build)

    async def _finish(
        self, owner_id: UUID, presentation_id: UUID, working: Presentation
    ) -> Presentation:
        indexed_slides: list[Slide] = []
        searchable: list[str] = []
        pages: list[int | None] = []
        slides: list[int] = []
        for slide in working.slides:
            content = await self.presentations.take_bytes(owner_id, presentation_id, slide.id)
            text, phrase, latex = await self._recognize(owner_id, slide, content)
            indexed = slide.mark_indexed(text, phrase, latex)
            indexed_slides.append(indexed)
            piece = (phrase or text).strip()
            if not indexed.empty and piece:
                searchable.append(piece)
                pages.append(indexed.pdf_page)
                slides.append(indexed.position)
        ready = working.ready(tuple(indexed_slides), len(searchable))
        extracted = ExtractedText.compose("\n\n".join(searchable)).value
        await self.pieces.replace(
            presentation_id, tuple(searchable), extracted, tuple(pages), tuple(slides)
        )
        await self.presentations.clear_bytes(owner_id, presentation_id)
        await self.presentations.save(owner_id, ready)
        await self.intake.upsert(owner_id, material_row(ready))
        return ready

    async def _fail(self, owner_id: UUID, working: Presentation, reason: str) -> Presentation:
        failed = working.failed(reason)
        try:
            await self.pieces.replace(working.id, (), "")
        except StoreUnavailable:
            pass
        await self.presentations.clear_bytes(owner_id, working.id)
        await self.presentations.save(owner_id, failed)
        await self.intake.upsert(owner_id, material_row(failed))
        return failed

    async def _recognize(
        self, owner_id: UUID, slide: Slide, content: bytes | None
    ) -> tuple[str, str, str]:
        text = await self._slide_text(owner_id, slide, content)
        if not content or not is_weak_ocr(text, len(content)):
            return text, "", ""
        try:
            enriched = await self.formulas.enrich(slide.id, content, text)
        except Exception:
            return text, "", ""
        if enriched is None:
            return text, "", ""
        phrase, latex = enriched
        return text, phrase or "", latex or ""

    async def _slide_text(self, owner_id: UUID, slide: Slide, content: bytes | None) -> str:
        if content:
            try:
                read = await self.ocr.read(slide.id, content)
            except Exception as error:
                raise OcrUnavailable() from error
            text = slide.text.strip()
            if text and read.strip():
                return f"{text}\n\n{read}".strip()
            return read if read.strip() else text
        if slide.text.strip():
            return slide.text
        if slide.source != "pdf_page" or slide.pdf_document_id is None or slide.pdf_page is None:
            return ""
        owned = await self.intake.get(owner_id, slide.pdf_document_id)
        if owned is None:
            return ""
        body = await self.files.get(slide.pdf_document_id)
        if body:
            read = await self.reader.read(body)
            return _page_text(read, slide.pdf_page)
        return await self._stored_page_text(slide.pdf_document_id, slide.pdf_page)

    async def _stored_page_text(self, pdf_document_id: UUID, page: int) -> str:
        placed = await self.pieces.placed(pdf_document_id)
        chunks = [piece.text for piece in placed if piece.page == page]
        return "\n\n".join(chunks)

    async def _owned(self, owner_id: UUID, presentation_id: UUID) -> Presentation:
        found = await self.presentations.get(owner_id, presentation_id)
        if found is None:
            raise PresentationNotFound()
        if found.status not in {"draft", "ready", "indexing"}:
            raise PresentationNotFound()
        return found


def _page_text(read: PdfRead, page: int) -> str:
    chunks = [span.text for span in read.spans if span.page == page]
    return "\n\n".join(chunks)
