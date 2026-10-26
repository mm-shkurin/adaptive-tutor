import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.backend
class TestNameOf255CharactersIsKeptUnchanged(AbstractBackendTest):
    """A name of 255 characters is kept unchanged.

    Given a signed-in person
    When the person submits a PDF whose name is 255 characters and contains letters outside ASCII
    Then the document is accepted
    And the stored name equals the submitted name byte for byte after canonical composition
    And the name the person reads back equals that stored name
    """

    def test_should_keep_a_255_character_non_ascii_name_unchanged(self, documents):
        """Given a signed-in person
        When the person submits a PDF whose name is 255 characters and contains letters outside ASCII
        Then the document is accepted
        And the stored name equals the submitted name byte for byte after canonical composition
        And the name the person reads back equals that stored name
        """
        documents.given_a_signed_in_person()
        documents.then_the_person_is_signed_in()
        documents.when_the_person_submits_a_pdf_whose_name_is_255_characters_with_letters_outside_ascii()
        documents.then_the_document_is_accepted()
        documents.then_the_stored_name_equals_the_submitted_name_after_canonical_composition()
        documents.when_the_person_reads_the_uploaded_document()
        documents.then_the_name_read_back_equals_the_stored_name()
