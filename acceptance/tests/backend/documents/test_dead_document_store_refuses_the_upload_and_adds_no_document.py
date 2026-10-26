import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.backend


class TestDeadDocumentStoreRefusesTheUploadAndAddsNoDocument(AbstractBackendTest):
    """A dead document store refuses the upload and adds no document.

    Given a signed-in person
    And the document store is down
    When the person submits a valid PDF
    Then the upload is refused
    And no document is stored
    And the document is not marked ready
    """

    def test_should_refuse_the_upload_and_add_no_document(self, documents):
        """Given a signed-in person
        And the document store is down
        When the person submits a valid PDF
        Then the upload is refused
        And no document is stored
        And the document is not marked ready
        """
        documents.given_a_signed_in_person()
        documents.then_the_person_is_signed_in()
        documents.given_the_document_store_is_down()
        documents.when_the_person_submits_a_valid_pdf()
        documents.then_the_upload_is_refused_as_store_unavailable()
        documents.then_no_document_is_stored()
        documents.then_the_document_is_not_marked_ready()
