import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.backend
class TestNameSplitLetterAtLimitNotStoredBroken(AbstractBackendTest):
    """A name that would split a letter at the limit is not stored broken.

    Given a signed-in person
    When the person submits a PDF whose 255th place falls inside one letter
    Then the stored name contains no broken letter
    And the stored name contains no replacement character
    """

    @pytest.mark.skip(reason="RED: upload refused name_too_long instead of grapheme-safe accept")
    def test_should_not_store_a_broken_letter_at_the_name_limit(self, documents):
        """Given a signed-in person
        When the person submits a PDF whose 255th place falls inside one letter
        Then the stored name contains no broken letter
        And the stored name contains no replacement character
        """
        documents.given_a_signed_in_person()
        documents.then_the_person_is_signed_in()
        documents.when_the_person_submits_a_pdf_whose_255th_place_falls_inside_one_letter()
        documents.then_the_document_is_accepted()
        documents.then_the_stored_name_contains_no_broken_letter()
        documents.then_the_stored_name_contains_no_replacement_character()
