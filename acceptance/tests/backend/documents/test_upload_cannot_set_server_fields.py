import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.backend
class TestUploadCannotSetServerFields(AbstractBackendTest):
    """An upload cannot set the server's fields.

    Given a signed-in person
    When the person submits a valid PDF and also sends an id, an owner, a status,
    a page count, a piece count, and an error
    Then the document is accepted only because the PDF itself is acceptable
    And the id is server-set
    And the owner is the signed-in person
    And the status is waiting
    And the page count is not the submitted count
    And the piece count is not the submitted count
    And the error is empty
    And a submitted byte size is ignored
    And a submitted upload time is ignored
    And the stored size is the file's byte count
    """

    def test_should_ignore_submitted_server_fields(self, documents):
        """Given a signed-in person
        When the person submits a valid PDF and also sends server-owned fields
        Then the response keeps server-set id, owner, status, counts, error, and size
        """
        documents.given_a_signed_in_person()
        documents.then_the_person_is_signed_in()
        documents.when_the_person_submits_a_valid_pdf_and_also_sends_server_fields()
        documents.then_the_document_is_accepted_and_server_fields_stay_untouched()
