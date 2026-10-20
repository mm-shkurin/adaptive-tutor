from uuid import UUID

from usecase.document.ports import DocumentIntake, PieceIndex


class SearchDocuments:
    def __init__(self, intake: DocumentIntake, pieces: PieceIndex):
        self.intake = intake
        self.pieces = pieces

    async def pieces_for(self, owner_id: UUID, document_id: UUID) -> tuple[str, ...]:
        raise NotImplementedError()

    async def extracted_text(self, owner_id: UUID, document_id: UUID) -> str:
        raise NotImplementedError()
