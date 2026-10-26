import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.skip(
    reason="RED: assert 'indexing' == 'failed' — search-store refusal leaves document indexing"
)
@pytest.mark.backend
class TestSearchStoreRefusalFailsDocument(AbstractBackendTest):
    """A search store that does not accept the index fails the document.

    Scenario Outline:
    Given an accepted document
    And the search store refuses
    When indexing runs
    Then the document is failed
    And the document is not ready
    And nothing from the file can be searched
    And the failure is visible on the document
    """

    def test_should_fail_the_document_when_the_search_store_refuses(self, documents):
        """Given an accepted document
        And the search store refuses
        When indexing runs
        Then the document is failed
        And the document is not ready
        And nothing from the file can be searched
        And the failure is visible on the document
        """
        documents.given_an_accepted_document()
        documents.and_the_search_store_refuses()
        documents.when_indexing_runs()
        documents.then_the_document_is_failed_after_indexing()
        documents.then_the_finished_document_is_not_ready()
        documents.then_nothing_from_the_file_can_be_searched()
        documents.then_the_failure_is_visible_on_the_document()
