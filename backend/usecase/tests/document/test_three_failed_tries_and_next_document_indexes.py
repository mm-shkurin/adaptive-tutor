import pytest


class TestThreeFailedTriesAndNextDocumentIndexes:
    """Three failed tries end as failed and the next document still indexes.

    Given a document whose indexing fails every time
    And a later valid document
    When indexing has been tried three times
    Then the failing document is failed
    And the later document still becomes ready
    """

    @pytest.mark.asyncio
    async def test_should_fail_after_three_tries_without_blocking_the_next_document(
        self, documents
    ):
        await documents.given_a_signed_in_person()
        await documents.given_a_document_whose_indexing_fails_every_time()
        await documents.and_a_later_valid_document()
        await documents.when_indexing_has_been_tried_three_times()
        await documents.then_the_failing_document_is_failed()
        await documents.then_the_later_document_still_becomes_ready()
