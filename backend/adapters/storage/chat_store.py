import asyncio
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import DBAPIError, IntegrityError, InterfaceError, OperationalError
from sqlalchemy.orm import selectinload

from adapters.persistence.tables import ChatLineRow, ChatRow, DocumentRow
from adapters.storage.chat_store_attempts import ChatStoreAttempts
from domain.chat.chat import Chat
from domain.document.document import DELETED_SOURCE_NAME
from usecase.chat.errors import ChatNotFound, StoreUnavailable


class PostgresChatStore(ChatStoreAttempts):
    def __init__(self, sessions, clock=None):
        self._sessions = sessions
        self._clock = clock
        self._attempt_locks: dict[tuple[UUID, str], asyncio.Lock] = {}
        self._chat_locks: dict[UUID, asyncio.Lock] = {}
        self._write_lock = asyncio.Lock()

    def _now(self) -> datetime:
        if self._clock is None:
            return datetime.now(timezone.utc)
        return self._clock.now()

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
                    .outerjoin(DocumentRow, DocumentRow.id == ChatRow.document_id)
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
                    .outerjoin(DocumentRow, DocumentRow.id == ChatRow.document_id)
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
            prior = {line.id: line.created_at for line in row.lines}
            stamped = self._now()
            row.lines.clear()
            row.lines.extend(
                ChatLineRow.from_line(
                    chat.id,
                    position,
                    line,
                    prior.get(line.id, stamped),
                )
                for position, line in enumerate(chat.lines)
            )

        await self._run(work)

    async def _owned(self, session, owner_id: UUID, chat_id: UUID) -> Chat | None:
        found = (
            await session.execute(
                select(ChatRow, DocumentRow.name)
                .outerjoin(DocumentRow, DocumentRow.id == ChatRow.document_id)
                .where(ChatRow.id == chat_id, ChatRow.owner_id == owner_id)
                .options(selectinload(ChatRow.lines))
            )
        ).one_or_none()
        if found is None:
            return None
        chat_row, name = found
        return self._chat(chat_row, name)

    def _chat(self, chat_row: ChatRow, name: str | None) -> Chat:
        lines = tuple(line.to_domain() for line in chat_row.lines)
        label = DELETED_SOURCE_NAME if name is None else name
        return Chat.stored(chat_row.id, chat_row.document_id, label, lines)

    async def person_send_times(self, owner_id: UUID) -> tuple[datetime, ...]:
        async def work(session):
            rows = (
                await session.execute(
                    select(ChatLineRow.created_at)
                    .join(ChatRow, ChatRow.id == ChatLineRow.chat_id)
                    .where(ChatRow.owner_id == owner_id, ChatLineRow.role == "person")
                    .order_by(ChatLineRow.created_at.asc())
                )
            ).scalars().all()
            return tuple(rows)

        return await self._run(work)

    async def _run(self, work):
        try:
            async with self._sessions() as session:
                async with session.begin():
                    return await work(session)
        except IntegrityError:
            raise
        except (OperationalError, InterfaceError, DBAPIError) as error:
            raise StoreUnavailable() from error
