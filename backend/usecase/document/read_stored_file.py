from uuid import UUID

from usecase.document.ports import FileStore


class ReadStoredFile:
    def __init__(self, files: FileStore):
        self.files = files

    async def content(self, document_id: UUID) -> bytes | None:
        return await self.files.get(document_id)
