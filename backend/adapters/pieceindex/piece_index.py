from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.exc import DBAPIError, IntegrityError, InterfaceError, OperationalError

from adapters.persistence.tables import DocumentExtractionRow, DocumentPieceRow
from usecase.document.ports import PieceIndex


class PostgresPieceIndex(PieceIndex):
    def __init__(self, sessions):
        self._sessions = sessions

    async def replace(self, document_id: UUID, pieces: tuple[str, ...], extracted: str) -> None:
        async def work(session):
            await session.execute(delete(DocumentPieceRow).where(DocumentPieceRow.document_id == document_id))
            await session.execute(
                delete(DocumentExtractionRow).where(DocumentExtractionRow.document_id == document_id)
            )
            session.add(DocumentExtractionRow(document_id=document_id, text=extracted))
            for ordinal, body in enumerate(pieces):
                session.add(DocumentPieceRow(document_id=document_id, ordinal=ordinal, body=body))

        await self._run(work)

    async def pieces(self, document_id: UUID) -> tuple[str, ...]:
        async def work(session):
            rows = await session.scalars(
                select(DocumentPieceRow)
                .where(DocumentPieceRow.document_id == document_id)
                .order_by(DocumentPieceRow.ordinal)
            )
            return tuple(row.body for row in rows)

        return await self._run(work)

    async def extracted(self, document_id: UUID) -> str:
        async def work(session):
            row = await session.get(DocumentExtractionRow, document_id)
            return "" if row is None else row.text

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
