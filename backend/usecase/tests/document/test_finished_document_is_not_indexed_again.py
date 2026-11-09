import pytest


class TestFinishedDocumentIsNotIndexedAgain:
    """A finished document is not indexed again.

    Given a document that is ready or failed
    When indexing is requested again for that document
    Then the document stays ready or failed
    And no second set of pieces is stored
    """

    @pytest.mark.asyncio
    @pytest.mark.parametrize("finished", ["ready", "failed"])
    async def test_should_not_index_a_finished_document_again(self, documents, finished):
        await documents.given_a_document_that_is_finished(finished)
        await documents.when_indexing_is_requested_again_for_that_document()
        await documents.then_the_document_stays_finished()
        await documents.then_no_second_set_of_pieces_is_stored()
