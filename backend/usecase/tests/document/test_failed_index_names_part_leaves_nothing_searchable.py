import pytest


class TestFailedIndexNamesPartLeavesNothingSearchable:
    """A failed index names the part and leaves nothing searchable.

    Given a signed-in person with a neighbour's document
    When indexing fails on one table after an earlier step succeeded
    Then the document is failed
    And the failure names that table
    And nothing from the file can be searched
    And no piece rows remain
    And the original file is gone
    And the neighbour's document and file are unchanged
    And a retry does not add a second set of pieces
    """

    @pytest.mark.asyncio
    async def test_should_fail_on_the_table_and_leave_nothing_searchable(self, documents):
        await documents.given_a_signed_in_person()
        await documents.given_a_neighbour_account()
        await documents.when_the_neighbour_submits_a_pdf()
        await documents.then_the_neighbour_upload_is_waiting()
        await documents.when_the_neighbour_document_is_indexed()
        await documents.then_the_neighbour_document_is_ready()
        await documents.when_the_neighbour_text_is_searched()
        await documents.then_the_neighbour_text_is_indexed()
        await documents.when_the_neighbours_file_is_read()
        await documents.then_the_neighbours_file_is_already_gone()
        await documents.when_indexing_fails_on_one_table_after_an_earlier_step_succeeded()
        await documents.then_the_document_is_failed()
        await documents.then_the_failure_names_that_table()
        await documents.then_nothing_from_the_file_can_be_searched()
        await documents.then_no_piece_rows_remain()
        await documents.when_the_original_file_is_read()
        await documents.then_the_original_file_is_gone()
        await documents.then_the_neighbours_document_and_file_are_unchanged()
        await documents.when_indexing_is_retried()
        await documents.then_a_retry_does_not_add_a_second_set_of_pieces()
