from usecase.document.ports import PdfReader


class PyPdfReader(PdfReader):
    async def read(self, content: bytes):
        raise NotImplementedError()
