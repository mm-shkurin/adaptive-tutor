import asyncio
from datetime import datetime
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.exc import DBAPIError, IntegrityError, InterfaceError, OperationalError
from sqlalchemy.orm import selectinload

from adapters.persistence.quiz_mapping import apply_state, new_row, quiz_from_row
from adapters.persistence.quiz_tables import QuizQuestionRow, QuizRow
from usecase.quiz.errors import DuplicateQuizKey, QuizNotFound, StoreUnavailable
from usecase.quiz.ports import LIST_CAP


class PostgresQuizStore:
    def __init__(self, sessions):
        self._sessions = sessions
        self._key_locks: dict[tuple[UUID, str], asyncio.Lock] = {}
        self._quiz_locks: dict[UUID, asyncio.Lock] = {}

    async def find_by_key(self, owner_id: UUID, key: str):
        async def work(session):
            row = await self._one(session, QuizRow.owner_id == owner_id, QuizRow.idempotency_key == key)
            return None if row is None else quiz_from_row(row)

        return await self._run(work)

    async def add(self, owner_id: UUID, quiz, created_at: datetime, key: str) -> None:
        async def work(session):
            session.add(new_row(owner_id, quiz, created_at, key))

        try:
            await self._run(work)
        except IntegrityError as error:
            raise DuplicateQuizKey() from error

    async def with_key(self, owner_id: UUID, key: str, build):
        lock = self._key_locks.setdefault((owner_id, key), asyncio.Lock())
        async with lock:
            found = await self.find_by_key(owner_id, key)
            if found is not None:
                return found
            return await build()

    async def list_for(self, owner_id: UUID):
        async def work(session):
            rows = (
                await session.scalars(
                    self._select()
                    .where(QuizRow.owner_id == owner_id)
                    .order_by(QuizRow.created_at.desc(), QuizRow.id.desc())
                    .limit(LIST_CAP)
                )
            ).all()
            return tuple(quiz_from_row(row) for row in rows)

        return await self._run(work)

    async def get(self, owner_id: UUID, quiz_id: UUID):
        async def work(session):
            row = await self._owned(session, owner_id, quiz_id)
            return None if row is None else quiz_from_row(row)

        return await self._run(work)

    async def update(self, owner_id: UUID, quiz_id: UUID, change):
        lock = self._quiz_locks.setdefault(quiz_id, asyncio.Lock())
        async with lock:
            async def work(session):
                row = await self._owned(session, owner_id, quiz_id)
                if row is None:
                    raise QuizNotFound()
                updated = change(quiz_from_row(row))
                apply_state(row, updated)
                return updated

            return await self._run(work)

    async def delete_owned(self, owner_id: UUID) -> None:
        async def work(session):
            await session.execute(delete(QuizRow).where(QuizRow.owner_id == owner_id))

        await self._run(work)

    async def _owned(self, session, owner_id: UUID, quiz_id: UUID):
        return await self._one(session, QuizRow.owner_id == owner_id, QuizRow.id == quiz_id)

    async def _one(self, session, *criteria):
        return await session.scalar(self._select().where(*criteria))

    def _select(self):
        return select(QuizRow).options(
            selectinload(QuizRow.questions).selectinload(QuizQuestionRow.choices),
            selectinload(QuizRow.answers),
            selectinload(QuizRow.attempt),
        )

    async def _run(self, work):
        try:
            async with self._sessions() as session:
                async with session.begin():
                    return await work(session)
        except IntegrityError:
            raise
        except (OperationalError, InterfaceError, DBAPIError) as error:
            raise StoreUnavailable() from error
