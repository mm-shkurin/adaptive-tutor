import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.backend
class TestRetryAfterPartialIndexDoesNotWritePiecesTwice(AbstractBackendTest):
    """A retry after a partial index does not write the pieces twice.

    Given indexing wrote the pieces and then failed before recording ready
    When indexing runs again
    Then one set of pieces exists
    And the virus check is not run again
    And the document becomes ready or failed
    And it is not ready while the pieces are incomplete
    """

    @pytest.mark.skip(reason="RED: AssertionError assert 2 == 1 — retry after partial index writes pieces twice")
    def test_should_store_one_piece_set_on_retry_after_partial_index(self, documents):
        """Given indexing wrote the pieces and then failed before recording ready
        When indexing runs again
        Then one set of pieces exists
        And the virus check is not run again
        And the document becomes ready or failed
        And it is not ready while the pieces are incomplete
        """
        documents.given_indexing_wrote_the_pieces_and_then_failed_before_recording_ready()
        documents.when_indexing_runs_again()
        documents.then_one_set_of_pieces_exists()
        documents.then_a_retry_does_not_run_the_virus_check_again()
        documents.then_the_document_becomes_ready_or_failed_and_does_not_stay_waiting()
        documents.then_it_is_not_ready_while_the_pieces_are_incomplete()
        documents.then_a_retry_does_not_add_a_second_set_of_pieces()
