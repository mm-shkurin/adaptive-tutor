import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.backend
class TestFailedIndexNamesPartLeavesNothingSearchable(AbstractBackendTest):
    """A failed index names the part and leaves nothing searchable.

    Given a signed-in person with a neighbour's document
    When indexing fails on one table after an earlier step succeeded
    Then the document is failed
    And the failure names that table
    And nothing from the file can be searched
    And no piece rows remain
    And the original file is gone
    And the neighbour's document and file are unchanged
    And a retry does not run the virus check again
    And a retry does not add a second set of pieces
    """

    def test_should_fail_on_the_table_and_leave_nothing_searchable(self, documents):
        """Given a signed-in person with a neighbour's document
        When indexing fails on one table after an earlier step succeeded
        Then the document is failed
        And the failure names that table
        And nothing from the file can be searched
        And no piece rows remain
        And the original file is gone
        And the neighbour's document and file are unchanged
        And a retry does not run the virus check again
        And a retry does not add a second set of pieces
        """
        documents.given_a_signed_in_person()
        documents.then_the_person_is_signed_in()
        documents.given_a_neighbour_account()
        documents.then_the_neighbour_is_signed_in()
        documents.when_the_neighbour_submits_a_pdf()
        documents.then_the_neighbour_upload_is_waiting()
        documents.when_the_neighbour_document_becomes_ready()
        documents.then_the_neighbour_document_is_ready()
        documents.when_indexing_fails_on_one_table_after_an_earlier_step_succeeded()
        documents.then_the_document_is_failed()
        documents.then_the_failure_names_that_table()
        documents.then_nothing_from_the_file_can_be_searched()
        documents.then_no_piece_rows_remain()
        documents.then_the_original_file_is_gone()
        documents.then_the_neighbours_document_and_file_are_unchanged()
        documents.when_indexing_is_retried()
        documents.then_a_retry_does_not_run_the_virus_check_again()
        documents.then_a_retry_does_not_add_a_second_set_of_pieces()
