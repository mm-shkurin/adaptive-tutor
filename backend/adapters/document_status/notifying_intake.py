from uuid import UUID

from domain.document.document import Document
from usecase.document.ports import DocumentIntake


class NotifyingDocumentIntake:
    """DocumentIntake decorator that publishes status changes to a hub."""

    def __init__(self, inner: DocumentIntake, hub):
        self._inner = inner
        self._hub = hub

    def __getattr__(self, name: str):
        return getattr(self._inner, name)

    async def find_by_key(self, owner_id: UUID, submission_key: str) -> Document | None:
        return await self._inner.find_by_key(owner_id, submission_key)

    async def store(
        self, owner_id: UUID, document: Document, content: bytes, submission_key: str
    ) -> None:
        await self._inner.store(owner_id, document, content, submission_key)
        self._hub.publish(owner_id, document)

    async def get(self, owner_id: UUID, document_id: UUID) -> Document | None:
        return await self._inner.get(owner_id, document_id)

    async def save(self, document: Document) -> None:
        await self._inner.save(document)
        await self._emit(document.id)

    async def next_waiting(self) -> tuple[Document, bytes] | None:
        claimed = await self._inner.next_waiting()
        if claimed is not None:
            await self._emit(claimed[0].id)
        return claimed

    async def list_page(
        self, owner_id: UUID, page: int, after: UUID | None = None
    ) -> tuple[tuple[Document, ...], bool]:
        return await self._inner.list_page(owner_id, page, after)

    async def _emit(self, document_id: UUID) -> None:
        owner_id = await self._owner_id(document_id)
        if owner_id is None:
            return
        current = await self._inner.get(owner_id, document_id)
        if current is not None:
            self._hub.publish(owner_id, current)

    async def _owner_id(self, document_id: UUID) -> UUID | None:
        lookup = getattr(self._inner, "owner_id_of", None)
        if lookup is None:
            return None
        return await lookup(document_id)
