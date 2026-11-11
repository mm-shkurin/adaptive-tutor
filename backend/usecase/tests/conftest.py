from datetime import datetime, timedelta, timezone

import pytest

pytest.register_assert_rewrite(
    "usecase.tests.statements.document_statements",
    "usecase.tests.statements.upload_rate_statements",
    "usecase.tests.statements.one_submission_statements",
    "usecase.tests.statements.indexing_claim_statements",
    "usecase.tests.statements.virus_check_statements",
    "usecase.tests.statements.call_deadline_statements",
    "usecase.tests.statements.hostile_name_statements",
    "usecase.tests.statements.partial_index_statements",
    "usecase.tests.statements.embedding_statements",
    "usecase.tests.statements.batch_retry_statements",
)

from usecase.document.list_documents import ListDocuments
from usecase.document.read_document import ReadDocument
from usecase.document.read_stored_file import ReadStoredFile
from usecase.document.search_documents import SearchDocuments
from usecase.document.submit_document import SubmitDocument
from usecase.tests.fake.document.fake_document_intake import FakeDocumentIntake
from usecase.tests.fake.document.fake_file_store import FakeFileStore
from usecase.tests.fake.document.fake_index_documents import FakeIndexDocuments
from usecase.tests.fake.document.fake_pdf_reader import FakePdfReader
from usecase.tests.fake.document.fake_piece_index import FakePieceIndex
from usecase.tests.fake.document.fake_upload_rate_limit import FakeUploadRateLimit
from usecase.tests.fake.document.fake_virus_check import FakeVirusCheck
from usecase.tests.statements.document_statements import DocumentStatements


class Clock:
    def __init__(self):
        self.moment = datetime(2024, 5, 6, 7, 8, 9, tzinfo=timezone.utc)

    def now(self):
        return self.moment

    def advance(self, seconds: int) -> None:
        self.moment += timedelta(seconds=seconds)


@pytest.fixture
def documents():
    bodies: dict = {}
    reader = FakePdfReader()
    intake = FakeDocumentIntake(bodies)
    files = FakeFileStore(bodies)
    pieces = FakePieceIndex()
    clock = Clock()
    rates = FakeUploadRateLimit(clock)
    virus = FakeVirusCheck()
    return DocumentStatements(
        SubmitDocument(intake, rates, virus),
        FakeIndexDocuments(intake, files, reader, pieces, clock),
        ReadDocument(intake),
        SearchDocuments(intake, pieces),
        ReadStoredFile(files),
        ListDocuments(intake),
        reader,
        rates,
        clock,
        pieces,
        virus,
    )
