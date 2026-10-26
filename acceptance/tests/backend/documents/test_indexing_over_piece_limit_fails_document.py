import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.skip(reason="RED: IndexDocuments marks over-limit PDF ready instead of failed")
@pytest.mark.backend
class TestIndexingOverPieceLimitFailsDocument(AbstractBackendTest):
    """Indexing that would store more than 2000 pieces fails the document.

    Given a signed-in person
    When the person submits a PDF that would store more than 2000 pieces
    Then the document is failed
    And nothing from the file can be searched
    """

    def test_should_fail_the_document_and_leave_nothing_searchable(self, documents):
        """Given a signed-in person
        When the person submits a PDF that would store more than 2000 pieces
        Then the document is failed
        And nothing from the file can be searched
        """
        documents.given_a_signed_in_person()
        documents.then_the_person_is_signed_in()
        documents.when_the_person_submits_a_pdf_that_would_store_more_than_2000_pieces()
        documents.when_the_many_pieces_document_finishes_indexing()
        documents.then_the_over_limit_document_is_failed()
        documents.then_nothing_from_the_file_can_be_searched()
