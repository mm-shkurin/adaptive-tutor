from uuid import UUID

from usecase.document.ports import DocumentIntake, PieceIndex


class SearchDocuments:
    def __init__(self, intake: DocumentIntake, pieces: PieceIndex):
        self.intake = intake
        self.pieces = pieces

    async def pieces_for(self, owner_id: UUID, document_id: UUID) -> tuple[str, ...]:
        if await self.intake.get(owner_id, document_id) is None:
            return ()
        return await self.pieces.pieces(document_id)

    async def extracted_text(self, owner_id: UUID, document_id: UUID) -> str:
        if await self.intake.get(owner_id, document_id) is None:
            return ""
        return await self.pieces.extracted(document_id)
