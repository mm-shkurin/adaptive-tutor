import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.backend
class TestIndexingUnfinishedInFiveMinutesIsFailed(AbstractBackendTest):
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

    def test_should_fail_when_indexing_exceeds_five_minutes(self, documents):
        """Given an accepted document that is still indexing
        When the clock is just short of five minutes
        Then the document is still indexing
        When five minutes have passed
        Then the document is failed
        And in-flight indexing is cancelled
        And nothing is stored after that instant
        And nothing from the file can be searched
        """
        documents.given_a_signed_in_person()
        documents.then_the_person_is_signed_in()
        documents.given_an_accepted_document_that_is_still_indexing()
        documents.when_the_clock_is_just_short_of_five_minutes()
        documents.then_the_document_is_still_indexing()
        documents.when_five_minutes_have_passed()
        documents.then_the_document_is_failed_after_five_minutes()
        documents.then_in_flight_indexing_is_cancelled()
        documents.then_nothing_is_stored_after_that_instant()
        documents.then_nothing_from_the_file_can_be_searched()
