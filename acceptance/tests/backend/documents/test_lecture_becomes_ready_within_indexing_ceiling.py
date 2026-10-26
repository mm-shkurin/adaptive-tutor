import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.backend
class TestLectureBecomesReadyWithinIndexingCeiling(AbstractBackendTest):
    """Load Test Scenario 1.1: A lecture becomes ready within the indexing ceiling.

    Given the standard indexing baseline
    When the person uploads that lecture
    Then the document becomes ready
    And indexing finishes within the indexing ceiling
    """

    def test_should_become_ready_within_the_indexing_ceiling(self, documents):
        """Given the standard indexing baseline
        When the person uploads that lecture
        Then the document becomes ready
        And indexing finishes within the indexing ceiling
        """
        documents.given_the_standard_indexing_baseline()
        documents.when_the_person_uploads_that_lecture()
        documents.then_the_document_becomes_ready()
        documents.then_indexing_finishes_within_the_indexing_ceiling()
