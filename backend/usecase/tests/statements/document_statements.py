from pathlib import Path
from uuid import uuid4

from usecase.document.index_documents import IndexDocuments
from usecase.document.indexing_budget import PIECE_CAP, TOKENS_PER_PIECE
from usecase.document.list_documents import ListDocuments
from usecase.document.ports import PdfRead
from usecase.document.read_document import ReadDocument
from usecase.document.read_stored_file import ReadStoredFile
from usecase.document.search_documents import SearchDocuments
from usecase.document.submit_document import AcceptedSubmission, SubmitDocument
from usecase.tests.fake.document.fake_index_documents import FakeIndexDocuments
from usecase.tests.fake.document.fake_pdf_reader import FakePdfReader
from usecase.tests.fake.document.fake_piece_index import FakePieceIndex
from usecase.tests.fake.document.fake_upload_rate_limit import FakeUploadRateLimit
from usecase.tests.scope.document_scope import DocumentScope
from usecase.tests.statements import document_views as views
from usecase.tests.statements.one_submission_statements import OneSubmissionStatements
from usecase.tests.statements.upload_rate_statements import UploadRateStatements

FIXTURES = Path(__file__).resolve().parents[4] / "acceptance" / "fixtures"
TABLE = "|Topic|Mark|\n|---|---|\n|Limits|91|\n"
TABLE_NAMED = "|Topic|Mark|\n|---|---|\n|Limits|91|"
FIVE_HUNDRED = (FIXTURES / "five_hundred.txt").read_text(encoding="utf-8")
JOINED = (FIXTURES / "joined.txt").read_text(encoding="utf-8")
EXTRACTED = (FIXTURES / "extracted.txt").read_text(encoding="utf-8")
NEIGHBOUR_TEXT = (FIXTURES / "neighbour.txt").read_text(encoding="utf-8")


class DocumentStatements(OneSubmissionStatements, UploadRateStatements):
    def __init__(
        self,
        submit: SubmitDocument,
        index: IndexDocuments,
        read: ReadDocument,
        search: SearchDocuments,
        stored: ReadStoredFile,
        listed: ListDocuments,
        reader: FakePdfReader,
        rates: FakeUploadRateLimit,
        clock,
        pieces: FakePieceIndex,
    ):
        self.submit = submit
        self.index = index
        self.read = read
        self.search = search
        self.stored = stored
        self.listed = listed
        self.rates = rates
        self.clock = clock
        self.pieces = pieces
        self.scope = DocumentScope.builder()
        self.lecture = (FIXTURES / "lecture.pdf").read_bytes()
        self.neighbour_pdf = (FIXTURES / "neighbour.pdf").read_bytes()
        self.many_pieces_pdf = b"%PDF-1.4 many-pieces-fixture"
        self.person_id = self.scope.person_id
        self.neighbour_id = self.scope.neighbour_id
        self.neighbour_upload = None
        self.neighbour_ready = None
        self.neighbour_pieces = None
        self.upload = None
        self.read_back = None
        self.ready = None
        self.finished = None
        self.lecture_pieces = None
        self.extracted = None
        self.original_file = None
        self.neighbour_file = None
        self.refusal = None
        self.race_results = None
        self.submission_key = None
        self.replay = None
        self.earlier = None
        self.second_upload = None
        self.piece_writes_before_retry = 0
        self._reader = reader
        reader.register(self.lecture, PdfRead(EXTRACTED, TABLE, views.PAGE_COUNT))
        reader.register(self.neighbour_pdf, PdfRead(NEIGHBOUR_TEXT, "", views.PAGE_COUNT))

    async def _accept(
        self, owner_id, name: str, content: bytes, submission_key: str | None = None
    ) -> AcceptedSubmission:
        key = str(uuid4()) if submission_key is None else submission_key
        return await self.submit.submit(owner_id, name, content, key)

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

    async def _assert_lecture_pieces(self) -> None:
        assert self.lecture_pieces == (FIVE_HUNDRED, JOINED)
