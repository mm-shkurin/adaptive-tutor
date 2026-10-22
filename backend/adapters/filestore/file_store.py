from uuid import UUID

from sqlalchemy.exc import DBAPIError, IntegrityError, InterfaceError, OperationalError

from adapters.persistence.tables import DocumentRow
from usecase.document.ports import FileStore


class PostgresFileStore(FileStore):
    def __init__(self, sessions):
        self._sessions = sessions

    async def put(self, document_id: UUID, content: bytes) -> None:
        async def work(session):
            row = await session.get(DocumentRow, document_id)
            if row is None:
                return
            row.body = content

        await self._run(work)

    async def get(self, document_id: UUID) -> bytes | None:
        async def work(session):
            row = await session.get(DocumentRow, document_id)
            if row is None or row.body is None:
                return None
            return bytes(row.body)

        return await self._run(work)

    async def delete(self, document_id: UUID) -> None:
        async def work(session):
            row = await session.get(DocumentRow, document_id)
            if row is None:
                return
            row.body = None

        await self._run(work)

    async def _run(self, work):
        try:
            async with self._sessions() as session:
                async with session.begin():
                    return await work(session)
        except IntegrityError:
            raise
        except (OperationalError, InterfaceError, DBAPIError) as error:
            from usecase.document.errors import StoreUnavailable

            raise StoreUnavailable() from error
