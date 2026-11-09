import asyncio
from datetime import datetime, timedelta, timezone
from uuid import UUID

from domain.document.document import Document
from usecase.document.errors import DuplicateSubmission, StoreUnavailable
from usecase.document.list_documents import PAGE_SIZE


class MemoryDocumentIntake:
    def __init__(self, bodies: dict[UUID, bytes] | None = None, probe=None, now=None):
        self.bodies = bodies if bodies is not None else {}
        self.rows: dict[UUID, tuple[UUID, Document]] = {}
        self._order: list[UUID] = []
        self._created_at: dict[UUID, datetime] = {}
        self._next_seq = 0
        self._keys: dict[tuple[UUID, str], UUID] = {}
        self._lock = asyncio.Lock()
        self._probe = probe
        self._now = now or (lambda: datetime.now(timezone.utc))
        self.dead = False
        self.live = 0

    async def find_by_key(self, owner_id: UUID, submission_key: str) -> Document | None:
        async def action():
            document_id = self._keys.get((owner_id, submission_key))
            if document_id is None:
                return None
            row = self.rows.get(document_id)
            return None if row is None else row[1]

        return await self._guard(action)

    async def store(
        self, owner_id: UUID, document: Document, content: bytes, submission_key: str
    ) -> None:
        async def action():
            async with self._lock:
                key = (owner_id, submission_key)
                if key in self._keys:
                    raise DuplicateSubmission()
                self._keys[key] = document.id
                self.rows[document.id] = (owner_id, document)
                self.bodies[document.id] = content
                self._next_seq += 1
                self._created_at[document.id] = self._now() + timedelta(microseconds=self._next_seq)
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
                current = row[1]
                if current.status in {"ready", "failed"} and document.status != current.status:
                    return current.status
                self.rows[document.id] = (row[0], document)
                return document.status

        status = await self._guard(action)
        if status == "indexing" and self._probe is not None:
            await asyncio.sleep(self._probe.indexing_hold_seconds())

    async def next_waiting(self) -> tuple[Document, bytes] | None:
        async def action():
            async with self._lock:
                peeked = self._first_waiting()
            if peeked is None:
                return None
            if self._probe is not None:
                await self._probe.synchronize_dual_claim(str(peeked.id))
            async with self._lock:
                return self._claim(peeked.id)

        return await self._guard(action)

    def _first_waiting(self) -> Document | None:
        for document_id in self._order:
            document = self.rows[document_id][1]
            if document.status == "waiting":
                return document
        return None

    def _claim(self, document_id: UUID) -> tuple[Document, bytes] | None:
        row = self.rows.get(document_id)
        if row is None or row[1].status != "waiting":
            return None
        claimed = row[1].indexing()
        self.rows[document_id] = (row[0], claimed)
        return claimed, self.bodies[document_id]

    async def list_page(
        self, owner_id: UUID, page: int, after: UUID | None = None
    ) -> tuple[tuple[Document, ...], bool]:
        async def action():
            owned = [
                document_id
                for document_id in self._order
                if self.rows[document_id][0] == owner_id
            ]
            owned.sort(
                key=lambda document_id: (self._created_at[document_id], document_id),
                reverse=True,
            )
            if after is not None and after in self._created_at and after in owned:
                cursor = (self._created_at[after], after)
                owned = [
                    document_id
                    for document_id in owned
                    if (self._created_at[document_id], document_id) < cursor
                ]
                window_ids = owned[: PAGE_SIZE + 1]
            else:
                start = (page - 1) * PAGE_SIZE
                window_ids = owned[start : start + PAGE_SIZE + 1]
            window = [self.rows[document_id][1] for document_id in window_ids]
            return tuple(window[:PAGE_SIZE]), len(window) > PAGE_SIZE

        return await self._guard(action)

    async def _guard(self, action):
        self.live += 1
        try:
            if self.dead:
                raise StoreUnavailable()
            return await action()
        finally:
            self.live -= 1
