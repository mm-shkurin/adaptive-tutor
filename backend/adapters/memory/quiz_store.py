import asyncio
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from domain.quiz.quiz import Quiz
from usecase.quiz.errors import DuplicateQuizKey, QuizNotFound, StoreUnavailable
from usecase.quiz.ports import LIST_CAP


@dataclass
class _Stored:
    owner_id: UUID
    quiz: Quiz
    created_at: datetime
    key: str


class MemoryQuizStore:
    def __init__(self):
        self.dead = False
        self.fail_next_add = False
        self.live = 0
        self.waiting = 0
        self._rows: list[_Stored] = []
        self._key_locks: dict[tuple[UUID, str], asyncio.Lock] = {}
        self._quiz_locks: dict[UUID, asyncio.Lock] = {}

    def held(self, owner_id: UUID) -> tuple[Quiz, ...]:
        return tuple(row.quiz for row in self._rows if row.owner_id == owner_id)

    def count(self) -> int:
        return len(self._rows)

    async def find_by_key(self, owner_id: UUID, key: str) -> Quiz | None:
        async def action():
            return self._by_key(owner_id, key)

        return await self._guard(action)

    async def add(self, owner_id: UUID, quiz: Quiz, created_at: datetime, key: str) -> None:
        async def action():
            if self.fail_next_add:
                self.fail_next_add = False
                raise StoreUnavailable()
            if self._by_key(owner_id, key) is not None:
                raise DuplicateQuizKey()
            self._rows.append(_Stored(owner_id, quiz, created_at, key))

        await self._guard(action)

    async def with_key(self, owner_id: UUID, key: str, build):
        lock = self._key_locks.setdefault((owner_id, key), asyncio.Lock())
        self.waiting += 1
        async with lock:
            self.waiting -= 1
            found = await self.find_by_key(owner_id, key)
            if found is not None:
                return found
            return await build()

    async def list_for(self, owner_id: UUID) -> tuple[Quiz, ...]:
        async def action():
            owned = [row for row in self._rows if row.owner_id == owner_id]
            owned.sort(key=lambda row: (row.created_at, row.quiz.id), reverse=True)
            return tuple(row.quiz for row in owned[:LIST_CAP])

        return await self._guard(action)

    async def get(self, owner_id: UUID, quiz_id: UUID) -> Quiz | None:
        async def action():
            return self._lookup(owner_id, quiz_id)

        return await self._guard(action)

    async def update(self, owner_id: UUID, quiz_id: UUID, change) -> Quiz:
        lock = self._quiz_locks.setdefault(quiz_id, asyncio.Lock())

        async def action():
            async with lock:
                current = self._lookup(owner_id, quiz_id)
                if current is None:
                    raise QuizNotFound()
                updated = change(current)
                self._replace(owner_id, updated)
                return updated

        return await self._guard(action)

    async def delete_owned(self, owner_id: UUID) -> None:
        async def action():
            self._rows = [row for row in self._rows if row.owner_id != owner_id]

        await self._guard(action)

    def _by_key(self, owner_id: UUID, key: str) -> Quiz | None:
        for row in self._rows:
            if row.owner_id == owner_id and row.key == key:
                return row.quiz
        return None

    def _lookup(self, owner_id: UUID, quiz_id: UUID) -> Quiz | None:
        for row in self._rows:
            if row.owner_id == owner_id and row.quiz.id == quiz_id:
                return row.quiz
        return None

    def _replace(self, owner_id: UUID, quiz: Quiz) -> None:
        for index, row in enumerate(self._rows):
            if row.owner_id == owner_id and row.quiz.id == quiz.id:
                self._rows[index] = _Stored(owner_id, quiz, row.created_at, row.key)
                return
        raise QuizNotFound()

    async def _guard(self, action):
        self.live += 1
        try:
            if self.dead:
                raise StoreUnavailable()
            return await action()
        finally:
            self.live -= 1
