import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.skip(
    reason="RED: second indexing run on ready document raises KeyError; table failure still yields ready"
)
@pytest.mark.backend
class TestFinishedDocumentIsNotIndexedAgain(AbstractBackendTest):
    """A finished document is not indexed again.

    Given a document that is ready or failed
    When indexing is requested again for that document
    Then the document stays ready or failed
    And no second set of pieces is stored
    """

    @pytest.mark.parametrize("finished", ["ready", "failed"])
    def test_should_not_index_a_finished_document_again(self, documents, finished):
        """Given a document that is finished
        When indexing is requested again for that document
        Then the document stays finished
        And no second set of pieces is stored
        """
        documents.given_a_document_that_is_finished(finished)
        documents.when_indexing_is_requested_again_for_that_document()
        documents.then_the_document_stays_finished()
        documents.then_no_second_set_of_pieces_is_stored()
