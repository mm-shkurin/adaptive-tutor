import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.backend
class TestUnknownStatusIsNotTreatedAsReady(AbstractBackendTest):
    """An unknown status is not treated as ready.

    Given an accepted document
    When the document is given a status that is not waiting, indexing, ready, or failed
    Then the document is not ready
    And nothing from the file is newly searchable
    """

    @pytest.mark.skip(reason="RED: SearchDocuments returns seeded pieces while document status is corrupted")
    def test_should_not_treat_an_unknown_status_as_ready(self, documents):
        """Given an accepted document
        When the document is given a status that is not waiting, indexing, ready, or failed
        Then the document is not ready
        And nothing from the file is newly searchable
        """
        documents.given_an_accepted_document()
        documents.when_the_document_is_given_a_status_that_is_not_waiting_indexing_ready_or_failed()
        documents.then_the_document_is_not_ready()
        documents.then_nothing_from_the_file_is_newly_searchable()
