from uuid import UUID

from usecase.document.ports import FileStore


class PostgresFileStore(FileStore):
    def __init__(self, sessions):
        self._sessions = sessions

    async def put(self, document_id: UUID, content: bytes) -> None:
        raise NotImplementedError()

    async def get(self, document_id: UUID) -> bytes | None:
        raise NotImplementedError()

    async def delete(self, document_id: UUID) -> None:
        raise NotImplementedError()
