import pytest

pytest.register_assert_rewrite("usecase.tests.statements.document_statements")

from usecase.document.index_documents import IndexDocuments
from usecase.document.read_document import ReadDocument
from usecase.document.read_stored_file import ReadStoredFile
from usecase.document.search_documents import SearchDocuments
from usecase.document.submit_document import SubmitDocument
from usecase.tests.fake.document.fake_document_intake import FakeDocumentIntake
from usecase.tests.fake.document.fake_file_store import FakeFileStore
from usecase.tests.fake.document.fake_pdf_reader import FakePdfReader
from usecase.tests.fake.document.fake_piece_index import FakePieceIndex
from usecase.tests.statements.document_statements import DocumentStatements


@pytest.fixture
def documents():
    bodies: dict = {}
    reader = FakePdfReader()
    intake = FakeDocumentIntake(bodies)
    files = FakeFileStore(bodies)
    pieces = FakePieceIndex()
    return DocumentStatements(
        SubmitDocument(intake),
        IndexDocuments(intake, files, reader, pieces),
        ReadDocument(intake),
        SearchDocuments(intake, pieces),
        ReadStoredFile(files),
        reader,
    )
