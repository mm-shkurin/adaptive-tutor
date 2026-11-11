from uuid import uuid4

from usecase.document.index_documents import IndexDocuments
from usecase.document.list_documents import ListDocuments
from usecase.document.ports import PdfRead
from usecase.document.read_document import ReadDocument
from usecase.document.read_stored_file import ReadStoredFile
from usecase.document.search_documents import SearchDocuments
from usecase.document.submit_document import AcceptedSubmission, SubmitDocument
from usecase.tests.fake.document.fake_pdf_reader import FakePdfReader
from usecase.tests.fake.document.fake_piece_index import FakePieceIndex
from usecase.tests.fake.document.fake_upload_rate_limit import FakeUploadRateLimit
from usecase.tests.fake.document.fake_virus_check import FakeVirusCheck
from usecase.tests.scope.document_scope import DocumentScope
from usecase.tests.statements import document_views as views
from usecase.tests.statements.batch_retry_statements import BatchRetryStatements
from usecase.tests.statements.call_deadline_statements import CallDeadlineStatements
from usecase.tests.statements.document_fixture_text import (
    EXTRACTED,
    FIVE_HUNDRED,
    FIXTURES,
    JOINED,
    NEIGHBOUR_TEXT,
    TABLE,
)
from usecase.tests.statements.embedding_statements import EmbeddingStatements
from usecase.tests.statements.hostile_name_statements import HostileNameStatements
from usecase.tests.statements.indexing_claim_statements import IndexingClaimStatements
from usecase.tests.statements.indexing_deadline_statements import IndexingDeadlineStatements
from usecase.tests.statements.indexing_fail_statements import IndexingFailStatements
from usecase.tests.statements.one_submission_statements import OneSubmissionStatements
from usecase.tests.statements.partial_index_statements import PartialIndexStatements
from usecase.tests.statements.ready_pdf_statements import ReadyPdfStatements
from usecase.tests.statements.search_store_statements import SearchStoreStatements
from usecase.tests.statements.upload_rate_statements import UploadRateStatements
from usecase.tests.statements.virus_check_statements import VirusCheckStatements


class DocumentStatements(
    ReadyPdfStatements,
    IndexingFailStatements,
    IndexingDeadlineStatements,
    IndexingClaimStatements,
    OneSubmissionStatements,
    UploadRateStatements,
    VirusCheckStatements,
    SearchStoreStatements,
    CallDeadlineStatements,
    HostileNameStatements,
    PartialIndexStatements,
    EmbeddingStatements,
    BatchRetryStatements,
):
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
        virus: FakeVirusCheck,
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
        self.virus = virus
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

    async def _assert_lecture_pieces(self) -> None:
        assert self.lecture_pieces == (FIVE_HUNDRED, JOINED)

