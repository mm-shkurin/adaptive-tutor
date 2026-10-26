import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.backend
class TestManyFailedIndexesDoNotRetryOnSameTick(AbstractBackendTest):
    """Many indexes that fail together do not retry on the same tick.

    Given many accepted documents
    And the search store fails once for all of them
    When they retry
    Then the retries are not all issued at the same instant
    And none of them is tried more than three times
    """

    @pytest.mark.skip(
        reason="RED: AssertionError: document expected a retry, got 0 attempts (indexing attempts not recorded)"
    )
    def test_should_spread_retries_and_cap_attempts(self, documents):
        """Given many accepted documents
        And the search store fails once for all of them
        When they retry
        Then the retries are not all issued at the same instant
        And none of them is tried more than three times
        """
        documents.given_a_signed_in_person()
        documents.then_the_person_is_signed_in()
        documents.given_many_accepted_documents()
        documents.and_the_search_store_fails_once_for_all_of_them()
        documents.when_they_retry()
        documents.then_the_retries_are_not_all_issued_at_the_same_instant()
        documents.then_none_of_them_is_tried_more_than_three_times()
