from usecase.tests.statements import document_views as views
from usecase.tests.statements.document_fixture_text import EXTRACTED, NEIGHBOUR_TEXT


class ReadyPdfStatements:
    async def given_a_signed_in_person(self) -> None:
        self.person_id = self.scope.person_id

    async def given_a_neighbour_account(self) -> None:
        self.neighbour_id = self.scope.neighbour_id

    async def when_the_neighbour_submits_a_pdf(self) -> None:
        self.neighbour_upload = (
            await self._accept(self.neighbour_id, self.scope.neighbour_name, self.neighbour_pdf)
        ).document

    async def then_the_neighbour_upload_is_waiting(self) -> None:
        assert self.neighbour_upload == views.waiting(
            self.neighbour_upload.id, self.scope.neighbour_name, len(self.neighbour_pdf)
        )

    async def when_the_neighbour_document_is_indexed(self) -> None:
        await self.index.index_waiting()
        self.neighbour_ready = await self.read.read(self.neighbour_id, self.neighbour_upload.id)

    async def then_the_neighbour_document_is_ready(self) -> None:
        assert self.neighbour_ready == views.neighbour_ready(
            self.neighbour_upload.id, self.scope.neighbour_name, len(self.neighbour_pdf)
        )

    async def when_the_neighbour_text_is_searched(self) -> None:
        self.neighbour_pieces = await self.search.pieces_for(self.neighbour_id, self.neighbour_upload.id)

    async def then_the_neighbour_text_is_indexed(self) -> None:
        assert self.neighbour_pieces == (NEIGHBOUR_TEXT,)

    async def when_the_person_submits_a_valid_pdf_that_contains_text_and_a_table(self) -> None:
        self.upload = (
            await self._accept(self.person_id, self.scope.lecture_name, self.lecture)
        ).document

    async def then_the_upload_is_answered_before_indexing_finishes(self) -> None:
        assert self.upload == views.waiting(self.upload.id, self.scope.lecture_name, len(self.lecture))

    async def when_the_person_reads_the_upload(self) -> None:
        self.read_back = await self.read.read(self.person_id, self.upload.id)

    async def then_the_next_read_shows_the_document_as_waiting_not_a_stale_copy(self) -> None:
        assert self.read_back == self.upload
        assert self.read_back == views.waiting(self.upload.id, self.scope.lecture_name, len(self.lecture))

    async def when_indexing_finishes(self) -> None:
        await self.index.index_waiting()
        self.ready = await self.read.read(self.person_id, self.upload.id)

    async def then_the_document_becomes_ready(self) -> None:
        assert self.ready == views.ready(self.upload.id, self.scope.lecture_name, len(self.lecture))

    async def then_the_ready_document_shows_the_file_name_size_pages_and_pieces(self) -> None:
        assert self.ready == views.ready(self.upload.id, self.scope.lecture_name, len(self.lecture))

    async def then_the_ready_document_has_no_failure_reason(self) -> None:
        assert self.ready == views.ready(self.upload.id, self.scope.lecture_name, len(self.lecture))

    async def when_the_person_searches_the_lecture(self) -> None:
        self.lecture_pieces = await self.search.pieces_for(self.person_id, self.upload.id)

    async def then_the_persons_search_finds_the_text_and_the_table(self) -> None:
        await self._assert_lecture_pieces()

    async def when_the_extracted_text_is_read(self) -> None:
        self.extracted = await self.search.extracted_text(self.person_id, self.upload.id)

    async def then_the_extracted_text_matches_after_canonical_composition(self) -> None:
        assert self.extracted == EXTRACTED

    async def when_the_neighbours_text_absence_is_checked(self) -> None:
        await self.when_the_person_searches_the_lecture()
        await self.when_the_extracted_text_is_read()
        await self.when_the_neighbour_text_is_searched()

    async def then_the_neighbours_text_is_absent(self) -> None:
        await self._assert_lecture_pieces()
        assert self.extracted == EXTRACTED
        assert self.neighbour_pieces == (NEIGHBOUR_TEXT,)

    async def then_a_piece_of_500_tokens_is_kept(self) -> None:
        await self._assert_lecture_pieces()

    async def then_a_shorter_piece_is_joined_onward(self) -> None:
        await self._assert_lecture_pieces()

    async def when_the_original_file_is_read(self) -> None:
        self.original_file = await self.stored.content(self.upload.id)

    async def then_the_original_file_is_gone(self) -> None:
        assert self.original_file is None

    async def when_the_neighbours_file_is_read(self) -> None:
        self.neighbour_file = await self.stored.content(self.neighbour_upload.id)

    async def then_the_neighbours_file_is_already_gone(self) -> None:
        assert self.neighbour_file is None
