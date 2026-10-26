import asyncio

from usecase.document.ports import PdfRead, PdfReader

from clients.application.index_probe import IndexProbe


class ProbeGatedPdfReader(PdfReader):
    def __init__(self, inner: PdfReader, probe: IndexProbe):
        self._inner = inner
        self._probe = probe

    async def read(self, content: bytes) -> PdfRead:
        while not self._probe.pdf_read_allowed():
            await asyncio.sleep(0.05)
        self._probe.enter_pdf_read()
        try:
            return await self._inner.read(content)
        finally:
            self._probe.exit_pdf_read()
