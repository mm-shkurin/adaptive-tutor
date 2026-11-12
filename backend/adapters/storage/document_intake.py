from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.exc import DBAPIError, IntegrityError, InterfaceError, OperationalError

from adapters.persistence.tables import DocumentRow
from domain.document.document import Document
from usecase.document.errors import DuplicateSubmission
from usecase.document.list_documents import PAGE_SIZE
from usecase.document.ports import DocumentIntake


class PostgresDocumentIntake(DocumentIntake):
    def __init__(self, sessions):
        self._sessions = sessions

    async def find_by_key(self, owner_id: UUID, submission_key: str) -> Document | None:
        async def work(session):
            row = await session.scalar(
                select(DocumentRow).where(
                    DocumentRow.owner_id == owner_id,
                    DocumentRow.idempotency_key == submission_key,
                )
            )
            return None if row is None else row.to_domain()

        return await self._run(work)

    async def store(
        self, owner_id: UUID, document: Document, content: bytes, submission_key: str
    ) -> None:
        async def work(session):
            row = DocumentRow(
                id=document.id,
                owner_id=owner_id,
                idempotency_key=submission_key,
                name=document.name,
                size_bytes=document.size_bytes,
                page_count=document.page_count,
                piece_count=document.piece_count,
                status=document.status,
                error=document.error,
                body=content,
                created_at=datetime.now(timezone.utc),
            )
            session.add(row)

        try:
            await self._run(work)
        except IntegrityError as error:
            raise DuplicateSubmission() from error

    async def get(self, owner_id: UUID, document_id: UUID) -> Document | None:
        async def work(session):
            row = await session.scalar(
                select(DocumentRow).where(
                    DocumentRow.id == document_id, DocumentRow.owner_id == owner_id
                )
            )
            return None if row is None else row.to_domain()

        return await self._run(work)

    async def owner_id_of(self, document_id: UUID) -> UUID | None:
        async def work(session):
            row = await session.get(DocumentRow, document_id)
            return None if row is None else row.owner_id

        return await self._run(work)

    async def save(self, document: Document) -> None:
        async def work(session):
            row = await session.scalar(
                select(DocumentRow)
                .where(DocumentRow.id == document.id)
                .with_for_update()
            )
            if row is None:
                return
            row.apply(document)

        await self._run(work)

    async def next_waiting(self) -> tuple[Document, bytes] | None:
        async def work(session):
            row = await session.scalar(
                select(DocumentRow)
                .where(DocumentRow.status == "waiting")
                .order_by(DocumentRow.created_at)
                .limit(1)
            )
            if row is None or row.body is None:
                return None
            result = await session.execute(
                update(DocumentRow)
                .where(DocumentRow.id == row.id, DocumentRow.status == "waiting")
                .values(status="indexing")
            )
            if result.rowcount != 1:
                return None
            return row.to_domain().indexing(), bytes(row.body)

        return await self._run(work)

    async def list_page(
        self, owner_id: UUID, page: int, after: UUID | None = None
    ) -> tuple[tuple[Document, ...], bool]:
        async def work(session):
            newest_first = (
                DocumentRow.created_at.desc(),
                DocumentRow.id.desc(),
            )
            query = select(DocumentRow).where(DocumentRow.owner_id == owner_id)
            if after is not None:
                cursor = await session.get(DocumentRow, after)
                if cursor is not None and cursor.owner_id == owner_id:
                    query = query.where(
                        (DocumentRow.created_at < cursor.created_at)
                        | (
                            (DocumentRow.created_at == cursor.created_at)
                            & (DocumentRow.id < cursor.id)
                        )
                    )
                rows = (
                    await session.scalars(query.order_by(*newest_first).limit(PAGE_SIZE + 1))
                ).all()
            else:
                rows = (
                    await session.scalars(
                        query.order_by(*newest_first)
                        .offset((page - 1) * PAGE_SIZE)
                        .limit(PAGE_SIZE + 1)
                    )
                ).all()
            return tuple(row.to_domain() for row in rows[:PAGE_SIZE]), len(rows) > PAGE_SIZE

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
