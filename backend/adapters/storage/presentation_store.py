import asyncio
from datetime import datetime
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.exc import DBAPIError, IntegrityError, InterfaceError, OperationalError
from sqlalchemy.orm import selectinload

from adapters.persistence.presentation_mapping import (
    apply_state,
    new_row,
    presentation_from_json,
    presentation_from_row,
)
from adapters.persistence.tables_presentations import (
    PresentationAddKeyRow,
    PresentationIndexKeyRow,
    PresentationRow,
    PresentationSlideBytesRow,
)
from domain.presentation.presentation import Presentation
from usecase.presentation.errors import PresentationNotFound, StoreUnavailable


class PostgresPresentationStore:
    def __init__(self, sessions):
        self._sessions = sessions
        self._locks: dict[UUID, asyncio.Lock] = {}

    async def add(self, owner_id: UUID, presentation: Presentation, created_at: datetime) -> None:
        async def work(session):
            session.add(new_row(owner_id, presentation, created_at))

        await self._run(work)

    async def get(self, owner_id: UUID, presentation_id: UUID) -> Presentation | None:
        async def work(session):
            row = await self._owned(session, owner_id, presentation_id)
            return None if row is None else presentation_from_row(row)

        return await self._run(work)

    async def save(self, owner_id: UUID, presentation: Presentation) -> None:
        async def work(session):
            row = await self._owned(session, owner_id, presentation.id)
            if row is None:
                raise PresentationNotFound()
            apply_state(row, presentation)

        await self._run(work)

    async def remove(self, owner_id: UUID, presentation_id: UUID) -> None:
        async def work(session):
            row = await self._owned(session, owner_id, presentation_id)
            if row is None:
                raise PresentationNotFound()
            await session.delete(row)

        await self._run(work)

    async def with_add_key(self, owner_id: UUID, presentation_id: UUID, key: str, build):
        result, _replayed = await self._idem(owner_id, presentation_id, key, "add", build)
        return result

    async def with_index_key(self, owner_id: UUID, presentation_id: UUID, key: str, build):
        return await self._idem(owner_id, presentation_id, key, "index", build)

    async def put_bytes(self, owner_id: UUID, presentation_id: UUID, slide_id: UUID, content: bytes) -> None:
        async def work(session):
            if await self._owned(session, owner_id, presentation_id) is None:
                raise PresentationNotFound()
            await session.merge(
                PresentationSlideBytesRow(presentation_id=presentation_id, slide_id=slide_id, body=content)
            )

        await self._run(work)

    async def take_bytes(self, owner_id: UUID, presentation_id: UUID, slide_id: UUID) -> bytes | None:
        async def work(session):
            if await self._owned(session, owner_id, presentation_id) is None:
                raise PresentationNotFound()
            row = await session.get(
                PresentationSlideBytesRow, {"presentation_id": presentation_id, "slide_id": slide_id}
            )
            return None if row is None else bytes(row.body)

        return await self._run(work)

    async def clear_bytes(self, owner_id: UUID, presentation_id: UUID) -> None:
        async def work(session):
            if await self._owned(session, owner_id, presentation_id) is None:
                raise PresentationNotFound()
            await session.execute(
                delete(PresentationSlideBytesRow).where(PresentationSlideBytesRow.presentation_id == presentation_id)
            )

        await self._run(work)

    async def has_bytes(self, owner_id: UUID, presentation_id: UUID, slide_id: UUID) -> bool:
        async def work(session):
            if await self._owned(session, owner_id, presentation_id) is None:
                return False
            row = await session.get(
                PresentationSlideBytesRow, {"presentation_id": presentation_id, "slide_id": slide_id}
            )
            return row is not None

        return await self._run(work)

    async def _idem(self, owner_id, presentation_id, key, lane, build):
        lock = self._locks.setdefault(presentation_id, asyncio.Lock())
        async with lock:
            if await self._must(owner_id, presentation_id) is None:
                raise PresentationNotFound()
            cached = await self._load_snapshot(owner_id, presentation_id, key, lane)
            if cached is not None:
                return cached, lane == "index"
            result = await build()
            await self._store_snapshot(owner_id, presentation_id, key, lane, result)
            return result, False

    async def _must(self, owner_id: UUID, presentation_id: UUID) -> bool:
        return (await self.get(owner_id, presentation_id)) is not None

    async def _load_snapshot(self, owner_id, presentation_id, key, lane):
        model = PresentationAddKeyRow if lane == "add" else PresentationIndexKeyRow

        async def work(session):
            row = await session.get(model, {"owner_id": owner_id, "presentation_id": presentation_id, "key": key})
            return None if row is None else presentation_from_json(row.snapshot)

        return await self._run(work)

    async def _store_snapshot(self, owner_id, presentation_id, key, lane, presentation: Presentation):
        model = PresentationAddKeyRow if lane == "add" else PresentationIndexKeyRow
        payload = presentation.json()

        async def work(session):
            session.add(
                model(owner_id=owner_id, presentation_id=presentation_id, key=key, snapshot=payload)
            )

        try:
            await self._run(work)
        except IntegrityError:
            pass

    async def _owned(self, session, owner_id: UUID, presentation_id: UUID):
        return await session.scalar(
            select(PresentationRow)
            .where(PresentationRow.id == presentation_id, PresentationRow.owner_id == owner_id)
            .options(selectinload(PresentationRow.slides))
        )

    async def _run(self, work):
        try:
            async with self._sessions() as session:
                async with session.begin():
                    return await work(session)
        except PresentationNotFound:
            raise
        except IntegrityError:
            raise
        except (OperationalError, InterfaceError, DBAPIError) as error:
            raise StoreUnavailable() from error