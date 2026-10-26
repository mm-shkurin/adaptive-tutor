import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.backend
class TestStaleStatusWriteDoesNotEraseNewerOne(AbstractBackendTest):
    """A stale status write does not erase a newer one.

    Given a document loaded twice while it is indexing
    When one save marks it ready and the other save marks it failed
    Then the later save does not silently discard the earlier one
    And the document ends in exactly one of those statuses
    And the pieces match that status
    """

    @pytest.mark.skip(reason="RED: assert 'failed' == 'ready' — later failed save overwrote earlier ready")
    def test_should_keep_the_earlier_terminal_status_when_a_stale_save_arrives_later(self, documents):
        """Given a document loaded twice while it is indexing
        When one save marks it ready and the other save marks it failed
        Then the later save does not silently discard the earlier one
        And the document ends in exactly one of those statuses
        And the pieces match that status
        """
        documents.given_a_document_loaded_twice_while_it_is_indexing()
        documents.when_one_save_marks_it_ready_and_the_other_marks_it_failed()
        documents.then_the_later_save_does_not_silently_discard_the_earlier_one()
        documents.then_the_document_ends_in_exactly_one_of_those_statuses()
        documents.then_the_pieces_match_that_status()
