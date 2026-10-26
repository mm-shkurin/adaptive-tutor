import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.backend
@pytest.mark.skip(reason="RED: illegal waiting→ready move returns 200 instead of 409")
class TestSkipOrReverseIndexingIsRefused(AbstractBackendTest):
    """A step that skips or reverses indexing is refused.

    Given a document that is waiting
    When the document is moved toward ready
    Then the move is refused
    And the document stays waiting
    And its pieces, its search entries, and its file are untouched
    """

    def test_should_refuse_skipping_from_waiting_to_ready(self, documents):
        """Given a document that is waiting
        When the document is moved toward ready
        Then the move is refused
        And the document stays waiting
        And its pieces, its search entries, and its file are untouched
        """
        documents.given_a_document_that_is_waiting()
        documents.when_the_document_is_moved_toward("ready")
        documents.then_the_move_is_refused()
        documents.then_the_document_stays_waiting()
        documents.then_its_pieces_its_search_entries_and_its_file_are_untouched()
