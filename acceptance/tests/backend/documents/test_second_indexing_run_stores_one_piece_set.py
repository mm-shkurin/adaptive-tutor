import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.skip(reason="RED: overlapping indexing runs write pieces twice (piece_write_count 2 not 1)")
@pytest.mark.backend
class TestSecondIndexingRunStoresOnePieceSet(AbstractBackendTest):
    """A second indexing run started while the first is going stores one set.

    Given indexing of a document is still running
    When a second indexing run starts for that document
    Then the two runs do not both write pieces
    And one set of pieces exists
    """

    def test_should_store_one_piece_set_when_second_run_starts_during_first(self, documents):
        """Given indexing of a document is still running
        When a second indexing run starts for that document
        Then the two runs do not both write pieces
        And one set of pieces exists
        """
        documents.given_indexing_of_a_document_is_still_running()
        documents.when_a_second_indexing_run_starts_for_that_document()
        documents.then_the_two_runs_do_not_both_write_pieces()
        documents.then_one_set_of_pieces_exists()
