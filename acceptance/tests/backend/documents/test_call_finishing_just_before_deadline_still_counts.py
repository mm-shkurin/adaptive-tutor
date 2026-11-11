import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.backend
class TestCallFinishingJustBeforeDeadlineStillCounts(AbstractBackendTest):
    """A call that finishes just before its deadline still counts.

    Given a virus check and a search store call
    When the call finishes just before its deadline
    Then it still counts as answered
    When the call reaches its deadline
    Then the virus check refuses the upload
    And the search store fails the document
    """

    def test_should_treat_just_before_deadline_as_answered_and_at_deadline_as_failure(self, documents):
        """Given a virus check and a search store call
        When the call finishes just before its deadline
        Then it still counts as answered
        When the call reaches its deadline
        Then the virus check refuses the upload
        And the search store fails the document
        """
        documents.given_a_signed_in_person()
        documents.then_the_person_is_signed_in()
        documents.given_a_virus_check_and_a_search_store_call()
        documents.when_the_virus_check_finishes_just_before_its_deadline()
        documents.when_the_person_submits_a_valid_pdf()
        documents.then_the_external_call_still_counts_as_answered_for_the_upload()

        documents.given_a_signed_in_person()
        documents.then_the_person_is_signed_in()
        documents.given_a_signed_in_person_with_one_document()
        documents.given_a_virus_check_and_a_search_store_call()
        documents.when_the_virus_check_reaches_its_deadline()
        documents.when_the_person_submits_a_pdf_for_virus_deadline_check()
        documents.then_the_upload_is_refused("virus_detected")

        documents.given_an_accepted_document()
        documents.when_the_search_store_call_finishes_just_before_its_deadline()
        documents.when_indexing_runs()
        documents.then_the_external_call_still_counts_as_answered_for_indexing()

        documents.given_an_accepted_document()
        documents.when_the_search_store_call_reaches_its_deadline()
        documents.when_indexing_runs()
        documents.then_the_search_store_fails_the_document()
