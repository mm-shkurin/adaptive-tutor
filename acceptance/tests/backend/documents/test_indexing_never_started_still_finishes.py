import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.backend
class TestIndexingNeverStartedStillFinishes(AbstractBackendTest):
    """A document whose indexing never started still finishes.

    Given an accepted document whose indexing was not started
    When indexing is due
    Then the document becomes ready or failed
    And it does not stay waiting
    """

    def test_should_finish_when_indexing_is_due(self, documents):
        """Given an accepted document whose indexing was not started
        When indexing is due
        Then the document becomes ready or failed
        And it does not stay waiting
        """
        documents.given_a_signed_in_person()
        documents.then_the_person_is_signed_in()
        documents.given_an_accepted_document_whose_indexing_was_not_started()
        documents.when_indexing_is_due()
        documents.then_the_document_becomes_ready_or_failed_and_does_not_stay_waiting()
