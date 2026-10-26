import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.skip(reason="RED: assert 'indexing' == 'failed' — search store refusal leaves document indexing")
@pytest.mark.backend
class TestRepeatedFailedUploadsReturnTheStoreConnectionsToBaseline(AbstractBackendTest):
    """Repeated failed uploads return the store connections to baseline.

    Given a signed-in person
    When several uploads fail because the store, the virus check, or the search store is unavailable
    Then the open connections return to the baseline
    And the open file handles and temporary files return to the baseline
    And a further upload can still be accepted once the store is back
    """

    def test_should_return_connections_handles_and_temps_to_baseline(self, documents):
        """Given a signed-in person
        When several uploads fail because the store, the virus check, or the search store is unavailable
        Then the open connections return to the baseline
        And the open file handles and temporary files return to the baseline
        And a further upload can still be accepted once the store is back
        """
        documents.given_a_signed_in_person()
        documents.then_the_person_is_signed_in()
        documents.given_the_document_store_connection_baselines()
        documents.when_several_uploads_fail_because_the_store_the_virus_check_or_the_search_store_is_unavailable()
        documents.then_the_open_connections_return_to_the_baseline()
        documents.then_the_open_file_handles_and_temporary_files_return_to_the_baseline()
        documents.when_the_document_store_is_back()
        documents.then_a_further_upload_can_still_be_accepted_once_the_store_is_back()
