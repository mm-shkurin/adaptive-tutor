from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import DBAPIError, IntegrityError, InterfaceError, OperationalError

from adapters.persistence.tables import DocumentRow
from domain.document.document import Document
from usecase.document.ports import DocumentIntake


class PostgresDocumentIntake(DocumentIntake):
    def __init__(self, sessions):
        self._sessions = sessions

    async def store(self, owner_id: UUID, document: Document, content: bytes) -> None:
        async def work(session):
            row = DocumentRow(
                id=document.id,
                owner_id=owner_id,
                name=document.name,
                size_bytes=document.size_bytes,
                page_count=document.page_count,
                piece_count=document.piece_count,
                status=document.status,
                error=document.error,
                body=content,
            )
            session.add(row)

        await self._run(work)

    async def get(self, owner_id: UUID, document_id: UUID) -> Document | None:
        async def work(session):
            row = await session.scalar(
                select(DocumentRow).where(
                    DocumentRow.id == document_id, DocumentRow.owner_id == owner_id
                )
            )
            return None if row is None else row.to_domain()

        return await self._run(work)

    async def save(self, document: Document) -> None:
        async def work(session):
            row = await session.get(DocumentRow, document.id)
            if row is None:
                return
            row.apply(document)

        await self._run(work)

    async def next_waiting(self) -> tuple[Document, bytes] | None:
        async def work(session):
            row = await session.scalar(
                select(DocumentRow).where(DocumentRow.status == "waiting").order_by(DocumentRow.id).limit(1)
            )
            if row is None:
                return None
            return row.to_domain(), bytes(row.body)

        return await self._run(work)

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
