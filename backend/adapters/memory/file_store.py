from uuid import UUID

from usecase.document.errors import StoreUnavailable


class MemoryFileStore:
    def __init__(self, bodies: dict[UUID, bytes], probe=None):
        self.bodies = bodies
        self._probe = probe
        self.dead = False

    async def put(self, document_id: UUID, content: bytes) -> None:
        if self.dead:
            raise StoreUnavailable()
        self.bodies[document_id] = content
        if self._probe is not None:
            self._probe.remember_file(str(document_id), content)

    async def get(self, document_id: UUID) -> bytes | None:
        if self.dead:
            raise StoreUnavailable()
        return self.bodies.get(document_id)

    async def delete(self, document_id: UUID) -> None:
        if self.dead:
            raise StoreUnavailable()
        self.bodies.pop(document_id, None)
        if self._probe is not None:
            self._probe.remove_file(str(document_id))
