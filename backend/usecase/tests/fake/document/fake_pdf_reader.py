import asyncio

from usecase.document.ports import PdfRead


class FakePdfReader:
    def __init__(self):
        self.reads: dict[bytes, PdfRead] = {}
        self._allowed = True

    def register(self, content: bytes, read: PdfRead) -> None:
        self.reads[content] = read

    def block(self) -> None:
        self._allowed = False

    def allow(self) -> None:
        self._allowed = True

    async def read(self, content: bytes) -> PdfRead:
        while not self._allowed:
            await asyncio.sleep(0.05)
        return self.reads[content]
