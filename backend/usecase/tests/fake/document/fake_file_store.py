from uuid import UUID


class FakeFileStore:
    def __init__(self, bodies: dict[UUID, bytes]):
        self.bodies = bodies

    async def put(self, document_id: UUID, content: bytes) -> None:
        self.bodies[document_id] = content

    async def get(self, document_id: UUID) -> bytes | None:
        return self.bodies.get(document_id)

    async def delete(self, document_id: UUID) -> None:
        self.bodies.pop(document_id, None)
