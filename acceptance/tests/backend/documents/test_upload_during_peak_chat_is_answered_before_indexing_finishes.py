import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.backend
class TestUploadDuringPeakChatIsAnsweredBeforeIndexingFinishes(AbstractBackendTest):
    """An upload during peak chat is answered before indexing finishes.

    Given the peak chat baseline
    When the person uploads a PDF
    Then the upload is answered before indexing finishes
    And the document later becomes ready
    """

    def test_should_answer_the_upload_before_indexing_finishes_during_peak_chat(self, documents):
        """Given the peak chat baseline
        When the person uploads a PDF
        Then the upload is answered before indexing finishes
        And the document later becomes ready
        """
        documents.given_a_signed_in_person_for_peak_chat_load()
        documents.then_the_person_is_signed_in()
        try:
            documents.given_the_peak_chat_baseline()
            documents.when_the_person_uploads_a_pdf()
            documents.then_the_upload_is_answered_before_indexing_finishes()
            documents.when_the_document_finishes_indexing()
            documents.then_the_document_becomes_ready_with_its_facts()
        finally:
            documents.when_the_peak_chat_finishes()
