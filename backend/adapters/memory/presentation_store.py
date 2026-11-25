import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from domain.presentation.presentation import Presentation
from usecase.presentation.errors import PresentationNotFound, StoreUnavailable


@dataclass
class _Row:
    owner_id: UUID
    presentation: Presentation
    created_at: datetime
    bodies: dict[UUID, bytes] = field(default_factory=dict)
    add_snapshots: dict[str, Presentation] = field(default_factory=dict)
    index_snapshots: dict[str, Presentation] = field(default_factory=dict)


class MemoryPresentationStore:
    def __init__(self):
        self.dead = False
        self.live = 0
        self._rows: dict[UUID, _Row] = {}
        self._locks: dict[UUID, asyncio.Lock] = {}

    async def add(self, owner_id: UUID, presentation: Presentation, created_at: datetime) -> None:
        async def action():
            self._rows[presentation.id] = _Row(owner_id, presentation, created_at)

        await self._guard(action)

    async def get(self, owner_id: UUID, presentation_id: UUID) -> Presentation | None:
        async def action():
            row = self._rows.get(presentation_id)
            if row is None or row.owner_id != owner_id:
                return None
            return row.presentation

        return await self._guard(action)

    async def save(self, owner_id: UUID, presentation: Presentation) -> None:
        async def action():
            row = self._rows.get(presentation.id)
            if row is None or row.owner_id != owner_id:
                raise PresentationNotFound()
            row.presentation = presentation

        await self._guard(action)

    async def remove(self, owner_id: UUID, presentation_id: UUID) -> None:
        async def action():
            row = self._rows.get(presentation_id)
            if row is None or row.owner_id != owner_id:
                raise PresentationNotFound()
            del self._rows[presentation_id]

        await self._guard(action)

    async def with_add_key(self, owner_id: UUID, presentation_id: UUID, key: str, build):
        result, _replayed = await self._idem(owner_id, presentation_id, key, "add", build)
        return result

    async def with_index_key(self, owner_id: UUID, presentation_id: UUID, key: str, build):
        return await self._idem(owner_id, presentation_id, key, "index", build)

    async def put_bytes(self, owner_id: UUID, presentation_id: UUID, slide_id: UUID, content: bytes) -> None:
        async def action():
            row = self._must(owner_id, presentation_id)
            row.bodies[slide_id] = content

        await self._guard(action)

    async def take_bytes(self, owner_id: UUID, presentation_id: UUID, slide_id: UUID) -> bytes | None:
        async def action():
            row = self._must(owner_id, presentation_id)
            return row.bodies.get(slide_id)

        return await self._guard(action)

    async def clear_bytes(self, owner_id: UUID, presentation_id: UUID) -> None:
        async def action():
            row = self._must(owner_id, presentation_id)
            row.bodies.clear()

        await self._guard(action)

    async def has_bytes(self, owner_id: UUID, presentation_id: UUID, slide_id: UUID) -> bool:
        async def action():
            row = self._rows.get(presentation_id)
            return row is not None and row.owner_id == owner_id and slide_id in row.bodies

        return await self._guard(action)

    def count(self) -> int:
        return len(self._rows)

    async def _idem(self, owner_id, presentation_id, key, lane, build):
        lock = self._locks.setdefault(presentation_id, asyncio.Lock())
        async with lock:
            row = self._rows.get(presentation_id)
            if row is None or row.owner_id != owner_id:
                raise PresentationNotFound()
            cache = row.add_snapshots if lane == "add" else row.index_snapshots
            if key in cache:
                replayed = lane == "index"
                return cache[key], replayed
            result = await build()
            cache[key] = result
            return result, False

    def _must(self, owner_id: UUID, presentation_id: UUID) -> _Row:
        row = self._rows.get(presentation_id)
        if row is None or row.owner_id != owner_id:
            raise PresentationNotFound()
        return row

    async def _guard(self, action):
        self.live += 1
        try:
            if self.dead:
                raise StoreUnavailable()
            return await action()
        finally:
            self.live -= 1