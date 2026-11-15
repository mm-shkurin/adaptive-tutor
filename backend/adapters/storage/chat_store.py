from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import DBAPIError, IntegrityError, InterfaceError, OperationalError
from sqlalchemy.orm import selectinload

from adapters.persistence.tables import ChatAttemptRow, ChatLineRow, ChatRow, DocumentRow
from domain.chat.chat import Chat
from usecase.chat.errors import ChatNotFound, StoreUnavailable
from usecase.chat.send_message import Attempt


class PostgresChatStore:
    def __init__(self, sessions):
        self._sessions = sessions

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
                error = {"code": row.error_code, "message": row.error_message}
            return Attempt(chat_id, lines, error)

        return await self._run(work)

    async def save_attempt(
        self, owner_id: UUID, chat_id: UUID, attempt_key: str, attempt: Attempt
    ) -> None:
        async def work(session):
            if await self._owned(session, owner_id, chat_id) is None:
                raise ChatNotFound()
            session.add(
                ChatAttemptRow(
                    chat_id=chat_id,
                    attempt_key=attempt_key,
                    line_ids=[str(line.id) for line in attempt.lines],
                    error_code=None if attempt.error is None else attempt.error["code"],
                    error_message=None if attempt.error is None else attempt.error["message"],
                )
            )

        await self._run(work)

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
        except ChatNotFound:
            raise
        except (OperationalError, InterfaceError, DBAPIError) as error:
            raise StoreUnavailable() from error
