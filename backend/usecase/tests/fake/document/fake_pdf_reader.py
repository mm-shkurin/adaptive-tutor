from usecase.document.ports import PdfRead


class FakePdfReader:
    def __init__(self):
        self.reads: dict[bytes, PdfRead] = {}

    def register(self, content: bytes, read: PdfRead) -> None:
        self.reads[content] = read

    async def read(self, content: bytes) -> PdfRead:
        return self.reads[content]
