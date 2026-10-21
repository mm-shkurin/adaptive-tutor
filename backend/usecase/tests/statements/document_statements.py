from pathlib import Path
from uuid import UUID

from domain.document.document import Document
from usecase.document.index_documents import IndexDocuments
from usecase.document.ports import PdfRead
from usecase.document.read_document import ReadDocument
from usecase.document.read_stored_file import ReadStoredFile
from usecase.document.search_documents import SearchDocuments
from usecase.document.submit_document import SubmitDocument
from usecase.tests.fake.document.fake_pdf_reader import FakePdfReader
from usecase.tests.scope.document_scope import DocumentScope

FIXTURES = Path(__file__).resolve().parents[4] / "acceptance" / "fixtures"
PAGE_COUNT = 1
PIECE_COUNT = 2
NEIGHBOUR_PIECE_COUNT = 1
TABLE = "|Topic|Mark|\n|---|---|\n|Limits|91|\n"
FIVE_HUNDRED = (FIXTURES / "five_hundred.txt").read_text(encoding="utf-8")
JOINED = (FIXTURES / "joined.txt").read_text(encoding="utf-8")
EXTRACTED = (FIXTURES / "extracted.txt").read_text(encoding="utf-8")
NEIGHBOUR_TEXT = (FIXTURES / "neighbour.txt").read_text(encoding="utf-8")


class DocumentStatements:
    def __init__(
        self,
        submit: SubmitDocument,
        index: IndexDocuments,
        read: ReadDocument,
        search: SearchDocuments,
        stored: ReadStoredFile,
        reader: FakePdfReader,
    ):
        self.submit = submit
        self.index = index
        self.read = read
        self.search = search
        self.stored = stored
        self.scope = DocumentScope.builder()
        self.lecture = (FIXTURES / "lecture.pdf").read_bytes()
        self.neighbour_pdf = (FIXTURES / "neighbour.pdf").read_bytes()
        self.person_id = self.scope.person_id
        self.neighbour_id = self.scope.neighbour_id
        self.neighbour_upload = None
        self.neighbour_ready = None
        self.neighbour_pieces = None
        self.upload = None
        self.read_back = None
        self.ready = None
        self.lecture_pieces = None
        self.extracted = None
        self.original_file = None
        self.neighbour_file = None
        reader.register(self.lecture, PdfRead(EXTRACTED, TABLE, PAGE_COUNT))
        reader.register(self.neighbour_pdf, PdfRead(NEIGHBOUR_TEXT, "", PAGE_COUNT))

    async def given_a_signed_in_person(self) -> None:
        self.person_id = self.scope.person_id

    async def given_a_neighbour_account(self) -> None:
        self.neighbour_id = self.scope.neighbour_id

    async def when_the_neighbour_submits_a_pdf(self) -> None:
        self.neighbour_upload = await self.submit.submit(
            self.neighbour_id, self.scope.neighbour_name, self.neighbour_pdf
        )

    async def then_the_neighbour_upload_is_waiting(self) -> None:
        assert self.neighbour_upload == self._neighbour_waiting(self.neighbour_upload.id)

    async def when_the_neighbour_document_is_indexed(self) -> None:
        await self.index.index_waiting()
        self.neighbour_ready = await self.read.read(self.neighbour_id, self.neighbour_upload.id)

    async def then_the_neighbour_document_is_ready(self) -> None:
        assert self.neighbour_ready == self._neighbour_ready(self.neighbour_upload.id)

    async def when_the_neighbour_text_is_searched(self) -> None:
        self.neighbour_pieces = await self.search.pieces_for(self.neighbour_id, self.neighbour_upload.id)

    async def then_the_neighbour_text_is_indexed(self) -> None:
        assert self.neighbour_pieces == (NEIGHBOUR_TEXT,)

    async def when_the_person_submits_a_valid_pdf_that_contains_text_and_a_table(self) -> None:
        self.upload = await self.submit.submit(self.person_id, self.scope.lecture_name, self.lecture)

    async def then_the_upload_is_answered_before_indexing_finishes(self) -> None:
        assert self.upload == self._waiting(self.upload.id)

    async def when_the_person_reads_the_upload(self) -> None:
        self.read_back = await self.read.read(self.person_id, self.upload.id)

    async def then_the_next_read_shows_the_document_as_waiting_not_a_stale_copy(self) -> None:
        assert self.read_back == self.upload
        assert self.read_back == self._waiting(self.upload.id)

    async def when_indexing_finishes(self) -> None:
        await self.index.index_waiting()
        self.ready = await self.read.read(self.person_id, self.upload.id)

    async def then_the_document_becomes_ready(self) -> None:
        assert self.ready == self._ready(self.upload.id)

    async def then_the_ready_document_shows_the_file_name_size_pages_and_pieces(self) -> None:
        assert self.ready == self._ready(self.upload.id)

    async def then_the_ready_document_has_no_failure_reason(self) -> None:
        assert self.ready == self._ready(self.upload.id)

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

    async def _assert_lecture_pieces(self) -> None:
        assert self.lecture_pieces == (FIVE_HUNDRED, JOINED)

    def _waiting(self, document_id: UUID) -> Document:
        return self._document(document_id, self.scope.lecture_name, len(self.lecture), None, None, "waiting")

    def _neighbour_waiting(self, document_id: UUID) -> Document:
        return self._document(
            document_id, self.scope.neighbour_name, len(self.neighbour_pdf), None, None, "waiting"
        )

    def _ready(self, document_id: UUID) -> Document:
        return self._document(
            document_id, self.scope.lecture_name, len(self.lecture), PAGE_COUNT, PIECE_COUNT, "ready"
        )

    def _neighbour_ready(self, document_id: UUID) -> Document:
        return self._document(
            document_id,
            self.scope.neighbour_name,
            len(self.neighbour_pdf),
            PAGE_COUNT,
            NEIGHBOUR_PIECE_COUNT,
            "ready",
        )

    def _document(
        self,
        document_id: UUID,
        name: str,
        size_bytes: int,
        page_count: int | None,
        piece_count: int | None,
        status: str,
    ) -> Document:
        return Document(
            id=document_id,
            name=name,
            size_bytes=size_bytes,
            page_count=page_count,
            piece_count=piece_count,
            status=status,
            error=None,
        )
