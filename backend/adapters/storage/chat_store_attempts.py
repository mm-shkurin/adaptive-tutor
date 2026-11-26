import asyncio
from uuid import UUID

from sqlalchemy.exc import IntegrityError

from adapters.persistence.tables import ChatAttemptRow
from adapters.storage.chat_attempt_commit import append_attempt
from usecase.chat.errors import ChatNotFound
from usecase.chat.send_message import Attempt, ReplyError


class ChatStoreAttempts:
    async def find_attempt(self, owner_id: UUID, chat_id: UUID, attempt_key: str) -> Attempt | None:
        async def work(session):
            chat = await self._owned(session, owner_id, chat_id)
            if chat is None:
                return None
            row = await session.get(ChatAttemptRow, {"chat_id": chat_id, "attempt_key": attempt_key})
            if row is None:
                return None
            by_id = {line.id: line for line in chat.lines}
            lines = tuple(by_id[UUID(str(line_id))] for line_id in row.line_ids)
            error = None
            if row.error_code is not None:
                error = ReplyError(row.error_code, row.error_message or "")
            return Attempt(chat_id, lines, error)

        return await self._run(work)

    async def save_attempt(
        self, owner_id: UUID, chat_id: UUID, attempt_key: str, attempt: Attempt
    ) -> None:
        async def work(session):
            if await self._owned(session, owner_id, chat_id) is None:
                raise ChatNotFound()
            error = attempt.error
            session.add(
                ChatAttemptRow(
                    chat_id=chat_id,
                    attempt_key=attempt_key,
                    line_ids=[str(line.id) for line in attempt.lines],
                    error_code=None if error is None else error.code,
                    error_message=None if error is None else error.message,
                )
            )

        await self._run(work)

    async def with_attempt(self, owner_id: UUID, chat_id: UUID, attempt_key: str, build):
        lock = self._attempt_locks.setdefault((chat_id, attempt_key), asyncio.Lock())
        async with lock:
            remembered = await self.find_attempt(owner_id, chat_id, attempt_key)
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
            remembered = await self.find_attempt(owner_id, chat_id, attempt_key)
            if remembered is not None:
                return remembered
            try:
                stamped = self._now()
                await self._run(
                    lambda session: append_attempt(
                        session, owner_id, chat_id, attempt_key, attempt, stamped
                    )
                )
            except IntegrityError:
                remembered = await self.find_attempt(owner_id, chat_id, attempt_key)
                if remembered is not None:
                    return remembered
                raise
            return attempt
