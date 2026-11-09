import asyncio
from datetime import datetime, timezone
from uuid import UUID

from domain.document.document import Document
from usecase.document.errors import DuplicateSubmission
from usecase.document.list_documents import PAGE_SIZE


class FakeDocumentIntake:
    def __init__(self, bodies: dict[UUID, bytes]):
        self.bodies = bodies
        self.rows: dict[UUID, tuple[UUID, Document]] = {}
        self._order: list[UUID] = []
        self._created_at: dict[UUID, datetime] = {}
        self._keys: dict[tuple[UUID, str], UUID] = {}
        self._tick = 0
        self._lock = asyncio.Lock()
        self._dual_claim_barrier: asyncio.Barrier | None = None

    def arm_dual_claim(self, parties: int = 2) -> None:
        self._dual_claim_barrier = asyncio.Barrier(parties)

    def disarm_dual_claim(self) -> None:
        self._dual_claim_barrier = None

    async def find_by_key(self, owner_id: UUID, submission_key: str) -> Document | None:
        document_id = self._keys.get((owner_id, submission_key))
        if document_id is None:
            return None
        row = self.rows.get(document_id)
        return None if row is None else row[1]

    async def store(
        self, owner_id: UUID, document: Document, content: bytes, submission_key: str
    ) -> None:
        key = (owner_id, submission_key)
        if key in self._keys:
            raise DuplicateSubmission()
        self._keys[key] = document.id
        self.rows[document.id] = (owner_id, document)
        self.bodies[document.id] = content
        self._tick += 1
        self._created_at[document.id] = datetime(2024, 1, 1, tzinfo=timezone.utc).replace(
            microsecond=self._tick
        )
        self._order.append(document.id)

    async def get(self, owner_id: UUID, document_id: UUID) -> Document | None:
        row = self.rows.get(document_id)
        if row is None or row[0] != owner_id:
            return None
        return row[1]

    async def save(self, document: Document) -> None:
        row = self.rows.get(document.id)
        if row is None:
            return
        self.rows[document.id] = (row[0], document)

    async def next_waiting(self) -> tuple[Document, bytes] | None:
        async with self._lock:
            peeked = self._first_waiting()
        if peeked is None:
            return None
        if self._dual_claim_barrier is not None:
            await self._dual_claim_barrier.wait()
        async with self._lock:
            return self._claim(peeked.id)

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
            cursor_at = self._created_at[after]
            owned = [
                document_id
                for document_id in owned
                if (self._created_at[document_id], document_id) < (cursor_at, after)
            ]
            window_ids = owned[: PAGE_SIZE + 1]
        else:
            start = (page - 1) * PAGE_SIZE
            window_ids = owned[start : start + PAGE_SIZE + 1]
        window = [self.rows[document_id][1] for document_id in window_ids]
        return tuple(window[:PAGE_SIZE]), len(window) > PAGE_SIZE
