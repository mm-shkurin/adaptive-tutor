import pytest


class TestSearchStoreThatDoesNotAcceptIndexFailsDocument:
    """A search store that does not accept the index fails the document.

    Scenario Outline:
    Given an accepted document
    And the search store <outcome>
    When indexing runs
    Then the document is failed
    And the document is not ready
    And nothing from the file can be searched
    And the failure is visible on the document
    """

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "outcome",
        [
            "times out",
            "refuses",
            "answers unreadable",
        ],
    )
    async def test_should_fail_the_document_when_the_search_store_does_not_accept(
        self, documents, outcome
    ):
        await documents.given_an_accepted_document()
        await documents.and_the_search_store(outcome)
        await documents.when_indexing_runs()
        await documents.then_the_document_is_failed_after_search_store()
        await documents.then_the_finished_document_is_not_ready()
        await documents.then_nothing_from_the_file_can_be_searched()
        await documents.then_the_failure_is_visible_on_the_document()
