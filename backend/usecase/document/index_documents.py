import asyncio
import contextlib
from dataclasses import replace
from datetime import datetime, timezone

from domain.document.document import Document
from domain.document.extracted_text import ExtractedText
from usecase.document.errors import StoreUnavailable
from usecase.document.indexing_budget import ATTEMPT_LIMIT, IndexingBudget, over_piece_cap
from usecase.document.ports import DocumentIntake, FileStore, PdfReader, PieceIndex

PAUSE = "pause"
RETRY = "retry"


class RetryIndex(Exception):
    """This attempt failed and another try is still allowed."""


class IndexDocuments:
    def __init__(self, intake: DocumentIntake, files: FileStore, reader: PdfReader, pieces: PieceIndex, clock=None):
        self.intake = intake
        self.files = files
        self.reader = reader
        self.pieces = pieces
        self._clock = clock or _WallClock()
        self._budget = IndexingBudget()

    async def index_waiting(self) -> None:
        claimed = await self.intake.next_waiting()
        if claimed is None:
            return
        await self._index(claimed[0], claimed[1])

    async def _index(self, document: Document, content: bytes) -> None:
        if document.status in {"ready", "failed"}:
            return
        if not self._budget.begin(document.id, self._clock.now()):
            return
        try:
            await self._run(document, content)
        finally:
            self._budget.finish(document.id)

    async def _run(self, document: Document, content: bytes) -> None:
        self._note_attempt(document)
        indexing = document if document.status == "indexing" else document.indexing()
        await self.intake.save(indexing)
        read = await self._read(document, content)
        if read is None or self._budget.cancelled(document.id):
            return
        reason = await self._refusal(document, read)
        if reason == PAUSE:
            return
        if reason == RETRY:
            await self._retry(document)
            return
        if reason:
            await self._fail(document, reason)
            return
        extracted = ExtractedText.compose(read.text)
        if over_piece_cap(0, extracted.value):
            await self._fail(document, "too many pieces")
            return
        parts = extracted.pieces()
        if over_piece_cap(len(parts), extracted.value):
            await self._fail(document, "too many pieces")
            return
        try:
            await self._store(document, parts, extracted.value)
        except RetryIndex:
            await self._retry(document)
            return
        except StoreUnavailable:
            await self._fail(document, "search store refused")
            return
        if await self._hold_ready(document):
            return
        stored = await self.pieces.pieces(document.id)
        count = len(stored) if stored else len(parts)
        await self.intake.save(indexing.ready(read.page_count, count))
        await self.files.delete(document.id)

    async def _read(self, document: Document, content: bytes):
        task = asyncio.create_task(self.reader.read(content))
        try:
            while not task.done():
                if self._budget.overdue(document.id, self._clock.now()):
                    self._budget.cancel(document.id)
                    task.cancel()
                    await self._fail(document, "indexing timed out")
                    return None
                await asyncio.sleep(0.05)
            return task.result()
        finally:
            if not task.done():
                task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await task

    async def _retry(self, document: Document) -> None:
        if self._budget.attempts(document.id) >= ATTEMPT_LIMIT:
            await self._fail(document, "indexing failed")
            return
        waiting = replace(document, status="waiting", error=None, page_count=None, piece_count=None)
        await self.intake.save(waiting)

    async def _fail(self, document: Document, reason: str) -> None:
        await self.intake.save(document.failed(reason))
        await self.files.delete(document.id)

    def _note_attempt(self, document: Document) -> None:
        return None

    async def _refusal(self, document: Document, read) -> str | None:
        return None

    async def _store(self, document: Document, parts: tuple[str, ...], extracted: str) -> None:
        existing = await self.pieces.pieces(document.id)
        if existing:
            return
        await self.pieces.replace(document.id, parts, extracted)

    async def _hold_ready(self, document: Document) -> bool:
        return False


class _WallClock:
    def now(self) -> datetime:
        return datetime.now(timezone.utc)
