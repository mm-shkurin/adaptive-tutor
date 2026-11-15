from uuid import UUID

from domain.chat.source import Source
from domain.document.placed_text import PlacedPiece
from usecase.document.errors import StoreUnavailable


class UnreadyMaterialSearch:
    async def ready(self, document_id: UUID) -> bool:
        return False

    async def matching(self, document_id: UUID, question: str) -> tuple[Source, ...]:
        return ()

    async def write(self, document_id: UUID, pieces: tuple[PlacedPiece, ...]) -> None:
        raise StoreUnavailable()
