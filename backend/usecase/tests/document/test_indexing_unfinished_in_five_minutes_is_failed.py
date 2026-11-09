import pytest


class TestIndexingUnfinishedInFiveMinutesIsFailed:
    """Indexing that has not finished in 5 minutes is failed.

    Given an accepted document that is still indexing
    When the clock is just short of five minutes
    Then the document is still indexing
    When five minutes have passed
    Then the document is failed
    And in-flight indexing is cancelled
    And nothing is stored after that instant
    And nothing from the file can be searched
    """

    @pytest.mark.asyncio
    async def test_should_fail_when_indexing_exceeds_five_minutes(self, documents):
        await documents.given_a_signed_in_person()
        await documents.given_an_accepted_document_that_is_still_indexing()
        await documents.when_the_clock_is_just_short_of_five_minutes()
        await documents.then_the_document_is_still_indexing()
        await documents.when_five_minutes_have_passed()
        await documents.then_the_document_is_failed_after_five_minutes()
        await documents.then_in_flight_indexing_is_cancelled()
        await documents.then_nothing_is_stored_after_that_instant()
        await documents.then_nothing_from_the_file_can_be_searched()
