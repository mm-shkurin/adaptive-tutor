import pytest


class TestStaleStatusWriteDoesNotEraseNewerOne:
    """A stale status write does not erase a newer one.

    Given a document loaded twice while it is indexing
    When one save marks it ready and the other save marks it failed
    Then the later save does not silently discard the earlier one
    And the document ends in exactly one of those statuses
    And the pieces match that status
    """

    @pytest.mark.asyncio
    async def test_should_keep_the_earlier_terminal_status_when_a_stale_save_arrives_later(
        self, documents
    ):
        """Given a document loaded twice while it is indexing
        When one save marks it ready and the other save marks it failed
        Then the later save does not silently discard the earlier one
        And the document ends in exactly one of those statuses
        And the pieces match that status
        """
        await documents.given_a_document_loaded_twice_while_it_is_indexing()
        await documents.when_one_save_marks_it_ready_and_the_other_marks_it_failed()
        await documents.then_the_later_save_does_not_silently_discard_the_earlier_one()
        await documents.then_the_document_ends_in_exactly_one_of_those_statuses()
        await documents.then_the_pieces_match_that_status()
