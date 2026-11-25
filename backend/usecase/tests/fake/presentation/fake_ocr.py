from uuid import UUID


class FakeOcr:
    def __init__(self):
        self.by_slide: dict[UUID, str] = {}
        self.default = "indexed text"

    def set_text(self, slide_id: UUID, text: str) -> None:
        self.by_slide[slide_id] = text

    async def read(self, slide_id: UUID, content: bytes) -> str:
        return self.by_slide.get(slide_id, self.default)