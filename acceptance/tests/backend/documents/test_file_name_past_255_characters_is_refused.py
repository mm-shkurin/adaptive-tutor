import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.backend
class TestFileNamePast255CharactersIsRefused(AbstractBackendTest):
    """A file name past 255 characters is refused.

    Given a signed-in person with one document
    When the person submits a PDF whose name is 256 characters
    Then the upload is refused
    And the list is unchanged
    """

    def test_should_refuse_a_pdf_whose_name_is_256_characters(self, documents):
        """Given a signed-in person with one document
        When the person submits a PDF whose name is 256 characters
        Then the upload is refused
        And the list is unchanged
        """
        documents.given_a_signed_in_person()
        documents.then_the_person_is_signed_in()
        documents.given_a_signed_in_person_with_one_document()
        documents.when_the_person_submits_a_pdf_whose_name_is_256_characters()
        documents.then_the_upload_is_refused("name_too_long")
        documents.then_the_list_is_unchanged()
