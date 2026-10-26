import asyncio
from uuid import UUID

from domain.document.document import Document
from usecase.document.list_documents import PAGE_SIZE
from usecase.document.errors import StoreUnavailable


class MemoryDocumentIntake:
    def __init__(self, bodies: dict[UUID, bytes] | None = None, probe=None):
        self.bodies = bodies if bodies is not None else {}
        self.rows: dict[UUID, tuple[UUID, Document]] = {}
        self._order: list[UUID] = []
        self._lock = asyncio.Lock()
        self._probe = probe
        self.dead = False

    async def store(self, owner_id: UUID, document: Document, content: bytes) -> None:
        async def action():
            async with self._lock:
                self.rows[document.id] = (owner_id, document)
                self.bodies[document.id] = content
                self._order.append(document.id)
                if self._probe is not None:
                    self._probe.remember_file(str(document.id), content)

        await self._guard(action)

    async def get(self, owner_id: UUID, document_id: UUID) -> Document | None:
        async def action():
            row = self.rows.get(document_id)
            if row is None or row[0] != owner_id:
                return None
            return row[1]

        return await self._guard(action)

    async def save(self, document: Document) -> None:
        async def action():
            async with self._lock:
                row = self.rows.get(document.id)
                if row is None:
                    return None
                self.rows[document.id] = (row[0], document)
                return document.status

        status = await self._guard(action)
        if status == "indexing" and self._probe is not None:
            await asyncio.sleep(self._probe.indexing_hold_seconds())

    async def next_waiting(self) -> tuple[Document, bytes] | None:
        async def action():
            async with self._lock:
                for document_id in self._order:
                    owner_id, document = self.rows[document_id]
                    if document.status == "waiting":
                        return document, self.bodies[document_id]
                return None

        return await self._guard(action)

    async def list_page(self, owner_id: UUID, page: int) -> tuple[tuple[Document, ...], bool]:
        async def action():
            owned = [
                self.rows[document_id][1]
                for document_id in reversed(self._order)
                if self.rows[document_id][0] == owner_id
            ]
            start = (page - 1) * PAGE_SIZE
            window = owned[start : start + PAGE_SIZE + 1]
            return tuple(window[:PAGE_SIZE]), len(window) > PAGE_SIZE

        return await self._guard(action)

    async def _guard(self, action):
        if self.dead:
            raise StoreUnavailable()
        return await action()
