from pathlib import Path

from usecase.document.ports import PdfRead
from usecase.tests.fake.document.fake_index_documents import FakeIndexDocuments
from usecase.tests.statements import document_views as views

FIXTURES = Path(__file__).resolve().parents[4] / "acceptance" / "fixtures"
HOSTILE_MARKUP = "' OR 1=1<script>"
HOSTILE_NAME = f"report{HOSTILE_MARKUP}\nline-two.pdf"
HOSTILE_FAILURE_REASON = f"{HOSTILE_MARKUP}\n|Topic|Mark|\n|---|---|\n|Limits|91|"
HOSTILE_PDF_TEXT = "' OR 1=1"
HOSTILE_PDF_BODY = "' OR 1=1 in pdf body"


class HostileNameStatements:
    async def when_the_person_uploads_a_pdf_whose_name_contains_query_metacharacters_and_markup(
        self,
    ) -> None:
        assert isinstance(self.index, FakeIndexDocuments)
        self.hostile_pdf = (FIXTURES / "hostile_query.pdf").read_bytes()
        self._reader.register(
            self.hostile_pdf, PdfRead(HOSTILE_PDF_BODY, "", views.PAGE_COUNT)
        )
        self.index.fail_table_after_text_step()
        self.hostile_submitted_name = HOSTILE_NAME
        self.upload = (
            await self._accept(self.person_id, HOSTILE_NAME, self.hostile_pdf)
        ).document
        self.stored_name = self.upload.name

    async def when_a_failed_documents_reason_contains_the_same(self) -> None:
        await self.index.index_waiting()
        self.finished = await self.read.read(self.person_id, self.upload.id)

    async def then_the_stored_name_equals_the_submitted_name(self) -> None:
        assert self.stored_name == self.hostile_submitted_name

    async def when_the_person_lists_documents(self) -> None:
        self.listed_page, _ = await self.listed.list(self.person_id, 1)

    async def then_the_list_shows_that_name_as_text(self) -> None:
        listed = next(
            document for document in self.listed_page if document.id == self.upload.id
        )
        assert listed.name == self.hostile_submitted_name

    async def then_the_failure_reason_is_shown_as_text(self) -> None:
        assert self.finished == views.failed(
            self.upload.id,
            self.hostile_submitted_name,
            len(self.hostile_pdf),
            HOSTILE_FAILURE_REASON,
        )

    async def then_the_markup_is_not_treated_as_a_control(self) -> None:
        assert "<script>" in self.stored_name
        assert "<script>" in self.finished.error

    async def then_the_query_metacharacters_are_not_treated_as_a_command(self) -> None:
        assert HOSTILE_MARKUP in self.stored_name
        assert HOSTILE_MARKUP in self.finished.error

    async def then_the_neighbours_documents_are_unchanged(self) -> None:
        await self.then_the_neighbours_document_and_file_are_unchanged()

    async def then_a_line_break_in_the_name_stays_inside_that_one_field(self) -> None:
        assert "\n" in self.stored_name
        read_back = await self.read.read(self.person_id, self.upload.id)
        assert read_back.name == self.hostile_submitted_name

    async def then_query_metacharacters_in_the_pdf_text_are_not_a_command(self) -> None:
        assert isinstance(self.index, FakeIndexDocuments)
        assert HOSTILE_PDF_TEXT in self.index.remembered_extracted(self.upload.id)
        assert await self.search.pieces_for(self.person_id, self.upload.id) == ()
