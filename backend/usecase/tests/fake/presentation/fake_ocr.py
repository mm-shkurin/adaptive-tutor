from uuid import UUID


class FakeOcr:
    def __init__(self):
        self.by_slide: dict[UUID, str] = {}
        self.default = "indexed text"
        self._failures: set[UUID | None] = set()

    def set_text(self, slide_id: UUID, text: str) -> None:
        self.by_slide[slide_id] = text

    def fail(self, slide_id: UUID | None = None) -> None:
        self._failures.add(slide_id)

    async def read(self, slide_id: UUID, content: bytes) -> str:
        if None in self._failures or slide_id in self._failures:
            raise ConnectionError("ocr channel failed")
        return self.by_slide.get(slide_id, self.default)
