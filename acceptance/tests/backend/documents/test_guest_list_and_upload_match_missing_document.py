import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.backend
class TestGuestListAndUploadMatchMissingDocument(AbstractBackendTest):
    """A guest's list and upload match a missing document.

    Given a guest
    When the guest reads the document list without the screen
    And the guest uploads a PDF without the screen
    Then each refusal matches a missing document
    And no document is added
    And neither answer includes a document name or text
    """

    def test_should_refuse_guest_list_and_upload_like_a_missing_document(self, documents):
        """Given a guest
        When the guest reads the document list without the screen
        And the guest uploads a PDF without the screen
        Then each refusal matches a missing document
        And no document is added
        And neither answer includes a document name or text
        """
        documents.given_a_guest()
        documents.when_a_missing_document_is_opened_without_the_screen()
        documents.when_the_guest_reads_the_document_list_without_the_screen()
        documents.when_the_guest_uploads_a_pdf_without_the_screen()
        documents.then_each_guest_refusal_matches_a_missing_document()
        documents.then_no_document_is_added()
        documents.then_neither_guest_answer_includes_a_document_name_or_text()
