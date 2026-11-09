import pytest

from tests.frontend.abstract_ui_test import AbstractUiTest


@pytest.mark.frontend
class TestRefusedUploadNamesTheReason(AbstractUiTest):
    """UI Test Scenario 2.2: A refused upload names the reason and leaves the list

    Given a signed-in person with a ready document
    When the person submits a file that is not a PDF
    Then the screen shows the file is not a PDF
    And the ready document is still the only row
    When the person submits a PDF over the maximum
    Then the screen shows the file is over 50 MB
    And the ready document is still the only row
    """

    def test_should_name_the_reason_and_leave_the_ready_row(
        self, signed_in_browser, document_library
    ):
        """UI Test Scenario 2.2: A refused upload names the reason and leaves the list

        Given a signed-in person with a ready document
        When the person submits a file that is not a PDF
        Then the screen shows the file is not a PDF
        And the ready document is still the only row
        When the person submits a PDF over the maximum
        Then the screen shows the file is over 50 MB
        And the ready document is still the only row
        """
        signed_in_browser.given_a_signed_in_person_with_a_ready_pdf_named_matanaliz()
        document_library.when_the_person_opens_documents()
        document_library.when_the_person_submits_a_file_that_is_not_a_pdf()
        document_library.then_the_screen_shows_the_file_is_not_a_pdf()
        document_library.then_the_ready_document_is_still_the_only_row()
        document_library.when_the_person_submits_a_pdf_over_the_maximum()
        document_library.then_the_screen_shows_the_file_is_over_50_mb()
        document_library.then_the_ready_document_is_still_the_only_row()
