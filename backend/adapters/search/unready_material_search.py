from uuid import UUID

from domain.chat.source import Source


class UnreadyMaterialSearch:
    async def ready(self, document_id: UUID) -> bool:
        return False

    async def matching(self, document_id: UUID, question: str) -> tuple[Source, ...]:
        return ()
