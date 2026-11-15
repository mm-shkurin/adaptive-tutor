import asyncio
import unicodedata

import pymupdf

from domain.document.placed_text import TextSpan
from usecase.document.ports import PdfRead, PdfReader


class PyPdfReader(PdfReader):
    async def read(self, content: bytes) -> PdfRead:
        return await asyncio.to_thread(_parse_pdf, content)


def _parse_pdf(content: bytes) -> PdfRead:
    document = pymupdf.open(stream=content, filetype="pdf")
    try:
        return _read_document(document)
    finally:
        document.close()


def _read_document(document) -> PdfRead:
    paragraphs: list[str] = []
    tables: list[str] = []
    paragraph_spans: list[TextSpan] = []
    table_spans: list[TextSpan] = []
    for page in document:
        number = page.number + 1
        page_paragraphs = _paragraphs_outside_tables(page)
        paragraphs.extend(page_paragraphs)
        paragraph_spans.extend(TextSpan(number, paragraph) for paragraph in page_paragraphs)
        page_tables = _markdown_tables(page)
        tables.extend(page_tables)
        table_spans.extend(TextSpan(number, table) for table in page_tables)
    body = unicodedata.normalize("NFC", "\n\n".join(paragraphs + tables))
    if tables:
        body = f"{body}\n"
    table = "".join(f"{piece}\n" for piece in tables)
    spans = tuple(TextSpan(span.page, unicodedata.normalize("NFC", span.text)) for span in paragraph_spans + table_spans)
    return PdfRead(body, table, document.page_count, spans)


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
