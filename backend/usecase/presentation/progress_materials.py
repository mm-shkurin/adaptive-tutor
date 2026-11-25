from uuid import UUID

from domain.document.document import Document
from usecase.document.ports import DocumentIntake

_CHIP_STATUSES = frozenset({"ready", "draft"})


class IntakeMaterials:
    def __init__(self, intake: DocumentIntake):
        self.intake = intake

    async def chips(self, owner_id: UUID) -> tuple[Document, ...]:
        return await self._all(owner_id, _is_chip)

    async def owned(self, owner_id: UUID, material_id: UUID) -> Document | None:
        return await self.intake.get(owner_id, material_id)

    async def _all(self, owner_id: UUID, keep) -> tuple[Document, ...]:
        page = 1
        after = None
        rows: list[Document] = []
        while True:
            batch, more = await self.intake.list_page(owner_id, page, after)
            rows.extend(document for document in batch if keep(document))
            if not more or not batch:
                break
            after = batch[-1].id
            page += 1
        return tuple(rows)


def _is_chip(document: Document) -> bool:
    if document.status not in _CHIP_STATUSES:
        return False
    return document.kind in {"pdf", "presentation"}