import asyncio
from datetime import datetime
from uuid import UUID

from domain.chat.chat import Chat
from usecase.chat.errors import ChatNotFound, StoreUnavailable
from usecase.chat.send_message import Attempt


class MemoryChatStore:
    def __init__(self):
        self.dead = False
        self.live = 0
        self._rows: list[tuple[UUID, Chat, datetime]] = []
        self._attempts: dict[tuple[UUID, UUID, str], Attempt] = {}
        self._write_lock = asyncio.Lock()
        self._attempt_locks: dict[tuple[UUID, str], asyncio.Lock] = {}
        self._chat_locks: dict[UUID, asyncio.Lock] = {}
        self._thread_interleave = None
        self._attempt_interleave = None

    def arm_thread_interleave(self, latch) -> None:
        self._thread_interleave = latch

    def arm_attempt_interleave(self, latch) -> None:
        self._attempt_interleave = latch

    async def add(self, owner_id: UUID, chat: Chat, created_at: datetime) -> None:
        async def action():
            self._rows.append((owner_id, chat, created_at))

        await self._guard(action)

    async def list_for(self, owner_id: UUID) -> tuple[Chat, ...]:
        async def action():
            owned = [row for row in self._rows if row[0] == owner_id]
            owned.sort(key=lambda row: (row[2], row[1].id), reverse=True)
            return tuple(row[1] for row in owned)

        return await self._guard(action)

    async def get(self, owner_id: UUID, chat_id: UUID) -> Chat | None:
        async def action():
            found = self._lookup(owner_id, chat_id)
            if self._thread_interleave is not None:
                await self._thread_interleave.after_read()
            return found

        return await self._guard(action)

    async def newest_for_document(self, owner_id: UUID, document_id: UUID) -> Chat | None:
        async def action():
            owned = [
                row
                for row in self._rows
                if row[0] == owner_id and row[1].document_id == document_id
            ]
            if not owned:
                return None
            owned.sort(key=lambda row: (row[2], row[1].id), reverse=True)
            return owned[0][1]

        return await self._guard(action)

    async def save(self, owner_id: UUID, chat: Chat) -> None:
        async def action():
            for index, (owner, stored, created) in enumerate(self._rows):
                if owner == owner_id and stored.id == chat.id:
                    self._rows[index] = (owner, chat, created)
                    return
            raise ChatNotFound()

        await self._guard(action)

    async def find_attempt(self, owner_id: UUID, chat_id: UUID, attempt_key: str) -> Attempt | None:
        async def action():
            found = self._attempts.get((owner_id, chat_id, attempt_key))
            if self._attempt_interleave is not None:
                await self._attempt_interleave.after_read()
            return found

        return await self._guard(action)

    async def save_attempt(
        self, owner_id: UUID, chat_id: UUID, attempt_key: str, attempt: Attempt
    ) -> None:
        async def action():
            if self._lookup(owner_id, chat_id) is None:
                raise ChatNotFound()
            self._attempts[(owner_id, chat_id, attempt_key)] = attempt

        await self._guard(action)

    async def with_attempt(self, owner_id: UUID, chat_id: UUID, attempt_key: str, build):
        lock = self._attempt_locks.setdefault((chat_id, attempt_key), asyncio.Lock())
        async with lock:
            remembered = self._attempts.get((owner_id, chat_id, attempt_key))
            if remembered is not None:
                return remembered
            return await build()

    async def with_chat(self, chat_id: UUID, work):
        lock = self._chat_locks.setdefault(chat_id, asyncio.Lock())
        async with lock:
            return await work()

    async def commit_attempt(
        self, owner_id: UUID, chat_id: UUID, attempt_key: str, attempt: Attempt
    ) -> Attempt:
        async with self._write_lock:

            async def action():
                remembered = self._attempts.get((owner_id, chat_id, attempt_key))
                if remembered is not None:
                    return remembered
                current = self._lookup(owner_id, chat_id)
                if current is None:
                    raise ChatNotFound()
                if attempt.persist and attempt.lines:
                    await self._save_unlocked(owner_id, current.with_appended(attempt.lines))
                self._attempts[(owner_id, chat_id, attempt_key)] = attempt
                return attempt

            return await self._guard(action)

    async def _save_unlocked(self, owner_id: UUID, chat: Chat) -> None:
        for index, (owner, stored, created) in enumerate(self._rows):
            if owner == owner_id and stored.id == chat.id:
                self._rows[index] = (owner, chat, created)
                return
        raise ChatNotFound()

    def _lookup(self, owner_id: UUID, chat_id: UUID) -> Chat | None:
        for owner, chat, _created in self._rows:
            if owner == owner_id and chat.id == chat_id:
                return chat
        return None

    async def _guard(self, action):
        self.live += 1
        try:
            if self.dead:
                raise StoreUnavailable()
            return await action()
        finally:
            self.live -= 1
