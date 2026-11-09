import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.backend
class TestThreeFailedTriesAndNextDocumentIndexes(AbstractBackendTest):
    """Three failed tries end as failed and the next document still indexes.

    Given a document whose indexing fails every time
    And a later valid document
    When indexing has been tried three times
    Then the failing document is failed
    And the later document still becomes ready
    """

    def test_should_fail_after_three_tries_without_blocking_the_next_document(self, documents):
        """Given a document whose indexing fails every time
        And a later valid document
        When indexing has been tried three times
        Then the failing document is failed
        And the later document still becomes ready
        """
        documents.given_a_signed_in_person()
        documents.then_the_person_is_signed_in()
        documents.given_a_document_whose_indexing_fails_every_time()
        documents.and_a_later_valid_document()
        documents.when_indexing_has_been_tried_three_times()
        documents.then_the_failing_document_is_failed()
        documents.then_the_later_document_still_becomes_ready()
