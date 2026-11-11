from usecase.document.indexing_budget import PIECE_CAP, TOKENS_PER_PIECE
from usecase.document.ports import PdfRead
from usecase.tests.fake.document.fake_index_documents import FakeIndexDocuments
from usecase.tests.statements import document_views as views
from usecase.tests.statements.document_fixture_text import NEIGHBOUR_TEXT, TABLE_NAMED


class IndexingFailStatements:
    async def when_indexing_fails_on_one_table_after_an_earlier_step_succeeded(self) -> None:
        assert isinstance(self.index, FakeIndexDocuments)
        self.index.fail_table_after_text_step()
        self.upload = (
            await self._accept(self.person_id, self.scope.lecture_name, self.lecture)
        ).document
        await self.index.index_waiting()
        self.finished = await self.read.read(self.person_id, self.upload.id)

    async def then_the_document_is_failed(self) -> None:
        assert self.finished == views.failed(
            self.upload.id, self.scope.lecture_name, len(self.lecture), TABLE_NAMED
        )

    async def then_the_failure_names_that_table(self) -> None:
        assert self.finished.error == TABLE_NAMED

    async def then_nothing_from_the_file_can_be_searched(self) -> None:
        assert await self.search.pieces_for(self.person_id, self.upload.id) == ()
        assert await self.search.extracted_text(self.person_id, self.upload.id) == ""

    async def then_no_piece_rows_remain(self) -> None:
        assert self.upload.id not in self.pieces.stored
        assert await self.pieces.pieces(self.upload.id) == ()

    async def then_the_neighbours_document_and_file_are_unchanged(self) -> None:
        assert self.neighbour_ready == views.neighbour_ready(
            self.neighbour_upload.id, self.scope.neighbour_name, len(self.neighbour_pdf)
        )
        assert await self.search.pieces_for(self.neighbour_id, self.neighbour_upload.id) == (
            NEIGHBOUR_TEXT,
        )
        assert await self.stored.content(self.neighbour_upload.id) is None

    async def when_indexing_is_retried(self) -> None:
        self.piece_writes_before_retry = len(self.pieces.stored.get(self.upload.id, ()))
        await self.index.index_waiting()
        self.finished = await self.read.read(self.person_id, self.upload.id)

    async def then_a_retry_does_not_add_a_second_set_of_pieces(self) -> None:
        assert len(self.pieces.stored.get(self.upload.id, ())) == self.piece_writes_before_retry
        assert self.finished == views.failed(
            self.upload.id, self.scope.lecture_name, len(self.lecture), TABLE_NAMED
        )

    async def given_a_document_whose_indexing_fails_every_time(self) -> None:
        assert isinstance(self.index, FakeIndexDocuments)
        self.failing = (
            await self._accept(self.person_id, "always-fails.pdf", self.neighbour_pdf)
        ).document
        self.index.fail_indexing_always(self.failing.id)

    async def and_a_later_valid_document(self) -> None:
        self.later = (
            await self._accept(self.person_id, self.scope.lecture_name, self.lecture)
        ).document

    async def when_indexing_has_been_tried_three_times(self) -> None:
        for _ in range(8):
            await self.index.index_waiting()
        self.failing_final = await self.read.read(self.person_id, self.failing.id)
        self.later_final = await self.read.read(self.person_id, self.later.id)

    async def then_the_failing_document_is_failed(self) -> None:
        assert self.failing_final == views.failed(
            self.failing.id, "always-fails.pdf", len(self.neighbour_pdf), "indexing failed"
        )

    async def then_the_later_document_still_becomes_ready(self) -> None:
        assert self.later_final == views.ready(
            self.later.id, self.scope.lecture_name, len(self.lecture)
        )

    async def when_the_person_submits_a_pdf_that_would_store_more_than_2000_pieces(self) -> None:
        overflow = "w " * (PIECE_CAP * TOKENS_PER_PIECE + 1)
        self._reader.register(
            self.many_pieces_pdf, PdfRead(overflow, "", views.PAGE_COUNT)
        )
        self.upload = (
            await self._accept(self.person_id, "many_pieces.pdf", self.many_pieces_pdf)
        ).document

    async def when_the_many_pieces_document_finishes_indexing(self) -> None:
        await self.index.index_waiting()
        self.finished = await self.read.read(self.person_id, self.upload.id)

    async def then_the_over_limit_document_is_failed(self) -> None:
        assert self.finished == views.failed(
            self.upload.id, "many_pieces.pdf", len(self.many_pieces_pdf), "too many pieces"
        )
