from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import DBAPIError, IntegrityError, InterfaceError, OperationalError

from adapters.persistence.tables import ChatRow, DocumentRow
from domain.chat.chat import Chat
from usecase.chat.errors import StoreUnavailable


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
                    .order_by(ChatRow.created_at.desc(), ChatRow.id.desc())
                )
            ).all()
            return tuple(
                Chat.stored(chat_row.id, chat_row.document_id, name) for chat_row, name in rows
            )

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
