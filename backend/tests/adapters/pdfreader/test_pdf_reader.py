import pytest
from pathlib import Path

from adapters.pdfreader.pdf_reader import PyPdfReader

FIXTURES = Path(__file__).parent.parent.parent.parent / "acceptance" / "fixtures"


@pytest.mark.skip(reason="RED: PdfReader adapter not implemented")
class TestPdfReader:
    """PdfReader adapter tests.

    Tests PDF text extraction, table extraction, and page counting.
    """

    @pytest.mark.asyncio
    async def test_should_extract_text_from_pdf(self):
        pdf_content = (FIXTURES / "lecture.pdf").read_bytes()
        reader = PyPdfReader()

        result = await reader.read(pdf_content)

        assert result.text == "Lecture content\n\nTable follows"

    @pytest.mark.asyncio
    async def test_should_extract_tables_from_pdf(self):
        pdf_content = (FIXTURES / "lecture.pdf").read_bytes()
        reader = PyPdfReader()

        result = await reader.read(pdf_content)

        assert result.table == "|Topic|Mark|\n|---|---|\n|Limits|91|\n"

    @pytest.mark.asyncio
    async def test_should_count_pages(self):
        pdf_content = (FIXTURES / "lecture.pdf").read_bytes()
        reader = PyPdfReader()

        result = await reader.read(pdf_content)

        assert result.page_count == 1
