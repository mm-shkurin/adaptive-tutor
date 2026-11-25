from datetime import datetime
from uuid import UUID

from domain.presentation.presentation import Presentation
from usecase.presentation.errors import PresentationNotFound, StoreUnavailable


class PostgresPresentationStore:
    """Persistence adapter placeholder; memory store covers tests."""

    async def add(self, owner_id: UUID, presentation: Presentation, created_at: datetime) -> None:
        raise StoreUnavailable()

    async def get(self, owner_id: UUID, presentation_id: UUID) -> Presentation | None:
        raise StoreUnavailable()

    async def save(self, owner_id: UUID, presentation: Presentation) -> None:
        raise StoreUnavailable()

    async def remove(self, owner_id: UUID, presentation_id: UUID) -> None:
        raise StoreUnavailable()

    async def with_add_key(self, owner_id: UUID, presentation_id: UUID, key: str, build):
        raise StoreUnavailable()

    async def with_index_key(self, owner_id: UUID, presentation_id: UUID, key: str, build):
        raise StoreUnavailable()

    async def put_bytes(self, owner_id: UUID, presentation_id: UUID, slide_id: UUID, content: bytes) -> None:
        raise StoreUnavailable()

    async def take_bytes(self, owner_id: UUID, presentation_id: UUID, slide_id: UUID) -> bytes | None:
        raise StoreUnavailable()

    async def clear_bytes(self, owner_id: UUID, presentation_id: UUID) -> None:
        raise StoreUnavailable()

    async def has_bytes(self, owner_id: UUID, presentation_id: UUID, slide_id: UUID) -> bool:
        raise PresentationNotFound()