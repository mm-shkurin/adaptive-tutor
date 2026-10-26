from pathlib import Path

import pytest

from adapters.pdfreader.pdf_reader import PyPdfReader

FIXTURES = Path(__file__).resolve().parents[3].parent / "acceptance" / "fixtures"
EXTRACTED = (FIXTURES / "extracted.txt").read_text(encoding="utf-8")
TABLE = "|Topic|Mark|\n|---|---|\n|Limits|91|\n"


class TestPdfReader:
    """PdfReader adapter tests.

    Tests PDF text extraction, table extraction, and page counting.
    """

    @pytest.mark.asyncio
    async def test_should_extract_text_from_pdf(self):
        pdf_content = (FIXTURES / "lecture.pdf").read_bytes()
        reader = PyPdfReader()

        result = await reader.read(pdf_content)

        assert result.text == EXTRACTED

    @pytest.mark.asyncio
    async def test_should_extract_tables_from_pdf(self):
        pdf_content = (FIXTURES / "lecture.pdf").read_bytes()
        reader = PyPdfReader()

        result = await reader.read(pdf_content)

        assert result.table == TABLE

    @pytest.mark.asyncio
    async def test_should_count_pages(self):
        pdf_content = (FIXTURES / "lecture.pdf").read_bytes()
        reader = PyPdfReader()

        result = await reader.read(pdf_content)

        assert result.page_count == 1
