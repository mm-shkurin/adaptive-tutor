from uuid import UUID

from domain.chat.source import REPLY_SOURCE_LIMIT, Source
from domain.document.placed_text import PlacedPiece
from usecase.document.ports import PieceIndex


class MemoryPieceVectors:
    def __init__(self, pieces: PieceIndex):
        self._pieces = pieces
        self.live = 0

    async def write(self, document_id: UUID, pieces: tuple[PlacedPiece, ...]) -> None:
        _ = document_id, pieces

    async def ready(self, document_id: UUID) -> bool:
        return len(await self._pieces.pieces(document_id)) > 0

    async def matching(self, document_id: UUID, question: str) -> tuple[Source, ...]:
        if question.strip() == "":
            return ()
        placed = await self._pieces.placed(document_id)
        return tuple(Source.from_placed(piece) for piece in placed[:REPLY_SOURCE_LIMIT])