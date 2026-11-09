import pytest


class TestPathologicalPdfDoesNotIndexPastFiveMinutes:
    """A pathological PDF does not keep indexing busy past five minutes.

    Given a signed-in person
    When the person submits a PDF that is costly to read but within the size limit
    Then indexing finishes or fails within five minutes
    And it does not keep running after that
    """

    @pytest.mark.asyncio
    async def test_should_finish_or_fail_within_five_minutes_and_stop(self, documents):
        """Given a signed-in person
        When the person submits a PDF that is costly to read but within the size limit
        Then indexing finishes or fails within five minutes
        And it does not keep running after that
        """
        await documents.given_a_signed_in_person()
        await documents.when_the_person_submits_a_pdf_that_is_costly_to_read_but_within_the_size_limit()
        await documents.then_indexing_finishes_or_fails_within_five_minutes()
        await documents.then_it_does_not_keep_running_after_that()
