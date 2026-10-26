import unicodedata

import pymupdf

from usecase.document.ports import PdfRead, PdfReader


class PyPdfReader(PdfReader):
    async def read(self, content: bytes) -> PdfRead:
        document = pymupdf.open(stream=content, filetype="pdf")
        try:
            return _read_document(document)
        finally:
            document.close()


def _read_document(document) -> PdfRead:
    paragraphs: list[str] = []
    tables: list[str] = []
    for page in document:
        paragraphs.extend(_paragraphs_outside_tables(page))
        tables.extend(_markdown_tables(page))
    body = unicodedata.normalize("NFC", "\n\n".join(paragraphs + tables))
    if tables:
        body = f"{body}\n"
    table = "".join(f"{piece}\n" for piece in tables)
    return PdfRead(body, table, document.page_count)


def _paragraphs_outside_tables(page) -> list[str]:
    table_boxes = [pymupdf.Rect(table.bbox) for table in page.find_tables().tables]
    paragraphs: list[str] = []
    for block in page.get_text("blocks"):
        if any(pymupdf.Rect(block[:4]).intersects(box) for box in table_boxes):
            continue
        paragraph = " ".join(line.strip() for line in block[4].rstrip("\n").splitlines() if line.strip())
        if paragraph:
            paragraphs.append(paragraph)
    return paragraphs


def _markdown_tables(page) -> list[str]:
    return [table.to_markdown().rstrip("\n") for table in page.find_tables().tables]
