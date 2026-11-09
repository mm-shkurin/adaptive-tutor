import pytest


class TestSecondIndexingRunStoresOnePieceSet:
    """A second indexing run started while the first is going stores one set.

    Given indexing of a document is still running
    When a second indexing run starts for that document
    Then the two runs do not both write pieces
    And one set of pieces exists
    """

    @pytest.mark.asyncio
    async def test_should_store_one_piece_set_when_second_run_starts_during_first(self, documents):
        """Given indexing of a document is still running
        When a second indexing run starts for that document
        Then the two runs do not both write pieces
        And one set of pieces exists
        """
        await documents.given_indexing_of_a_document_is_still_running()
        await documents.when_a_second_indexing_run_starts_for_that_document()
        await documents.then_the_two_runs_do_not_both_write_pieces()
        await documents.then_one_set_of_pieces_exists()
