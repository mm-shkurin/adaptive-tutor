import asyncio
from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import DBAPIError, IntegrityError, InterfaceError, OperationalError
from sqlalchemy.orm import selectinload

from adapters.persistence.tables import ChatAttemptRow, ChatLineRow, ChatRow, DocumentRow
from adapters.storage.chat_attempt_commit import append_attempt
from domain.chat.chat import Chat
from usecase.chat.errors import ChatNotFound, StoreUnavailable
from usecase.chat.send_message import Attempt, ReplyError


class PostgresChatStore:
    def __init__(self, sessions):
        self._sessions = sessions
        self._attempt_locks: dict[tuple[UUID, str], asyncio.Lock] = {}
        self._chat_locks: dict[UUID, asyncio.Lock] = {}
        self._write_lock = asyncio.Lock()

    async def add(self, owner_id: UUID, chat: Chat, created_at: datetime) -> None:
        async def work(session):
            session.add(
                ChatRow(
                    id=chat.id,
                    owner_id=owner_id,
                    document_id=chat.document_id,
                    created_at=created_at,
                )
            )

        await self._run(work)

    async def list_for(self, owner_id: UUID) -> tuple[Chat, ...]:
        async def work(session):
            rows = (
                await session.execute(
                    select(ChatRow, DocumentRow.name)
                    .join(DocumentRow, DocumentRow.id == ChatRow.document_id)
                    .where(ChatRow.owner_id == owner_id)
                    .options(selectinload(ChatRow.lines))
                    .order_by(ChatRow.created_at.desc(), ChatRow.id.desc())
                )
            ).all()
            return tuple(self._chat(chat_row, name) for chat_row, name in rows)

        return await self._run(work)

    async def get(self, owner_id: UUID, chat_id: UUID) -> Chat | None:
        async def work(session):
            return await self._owned(session, owner_id, chat_id)

        return await self._run(work)

    async def newest_for_document(self, owner_id: UUID, document_id: UUID) -> Chat | None:
        async def work(session):
            found = (
                await session.execute(
                    select(ChatRow, DocumentRow.name)
                    .join(DocumentRow, DocumentRow.id == ChatRow.document_id)
                    .where(ChatRow.owner_id == owner_id, ChatRow.document_id == document_id)
                    .options(selectinload(ChatRow.lines))
                    .order_by(ChatRow.created_at.desc(), ChatRow.id.desc())
                    .limit(1)
                )
            ).one_or_none()
            if found is None:
                return None
            chat_row, name = found
            return self._chat(chat_row, name)

        return await self._run(work)

    async def save(self, owner_id: UUID, chat: Chat) -> None:
        async def work(session):
            row = await session.scalar(
                select(ChatRow)
                .where(ChatRow.id == chat.id, ChatRow.owner_id == owner_id)
                .options(selectinload(ChatRow.lines))
            )
            if row is None:
                raise ChatNotFound()
            row.lines.clear()
            row.lines.extend(
                ChatLineRow.from_line(chat.id, position, line) for position, line in enumerate(chat.lines)
            )

        await self._run(work)

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
                await self._run(
                    lambda session: append_attempt(
                        session, owner_id, chat_id, attempt_key, attempt
                    )
                )
            except IntegrityError:
                remembered = await self.find_attempt(owner_id, chat_id, attempt_key)
                if remembered is not None:
                    return remembered
                raise
            return attempt

    async def _owned(self, session, owner_id: UUID, chat_id: UUID) -> Chat | None:
        found = (
            await session.execute(
                select(ChatRow, DocumentRow.name)
                .join(DocumentRow, DocumentRow.id == ChatRow.document_id)
                .where(ChatRow.id == chat_id, ChatRow.owner_id == owner_id)
                .options(selectinload(ChatRow.lines))
            )
        ).one_or_none()
        if found is None:
            return None
        chat_row, name = found
        return self._chat(chat_row, name)

    def _chat(self, chat_row: ChatRow, name: str) -> Chat:
        lines = tuple(line.to_domain() for line in chat_row.lines)
        return Chat.stored(chat_row.id, chat_row.document_id, name, lines)

    async def _run(self, work):
        try:
            async with self._sessions() as session:
                async with session.begin():
                    return await work(session)
        except IntegrityError:
            raise
        except (OperationalError, InterfaceError, DBAPIError) as error:
            raise StoreUnavailable() from error
