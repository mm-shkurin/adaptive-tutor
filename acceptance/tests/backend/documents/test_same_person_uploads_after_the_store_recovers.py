import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.backend
class TestSamePersonUploadsAfterTheStoreRecovers(AbstractBackendTest):
    """The same person uploads after the store recovers.

    Given the document store was down and is back
    When the person submits a valid PDF
    Then the document is accepted
    And the person can read it back
    """

    def test_should_accept_the_upload_and_return_it_on_read(self, documents):
        """Given the document store was down and is back
        When the person submits a valid PDF
        Then the document is accepted
        And the person can read it back
        """
        documents.given_a_signed_in_person()
        documents.then_the_person_is_signed_in()
        documents.given_the_document_store_was_down_and_is_back()
        documents.when_the_person_submits_a_valid_pdf()
        documents.then_the_document_is_accepted()
        documents.when_the_person_reads_the_uploaded_document()
        documents.then_the_person_can_read_it_back()
