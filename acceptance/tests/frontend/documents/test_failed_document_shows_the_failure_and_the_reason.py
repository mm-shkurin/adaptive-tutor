import pytest

from tests.frontend.abstract_ui_test import AbstractUiTest


@pytest.mark.frontend
class TestFailedDocumentShowsTheFailureAndTheReason(AbstractUiTest):
    """UI Test Scenario 2.3: A failed document shows the failure and the reason

    Given a signed-in person with a document that failed on page 12
    When the person opens documents
    Then the row shows «Не удалось»
    And the row shows that page 12 could not be read
    """

    def test_should_show_failed_and_the_page_12_reason(self, signed_in_browser, document_library):
        """UI Test Scenario 2.3: A failed document shows the failure and the reason

        Given a signed-in person with a document that failed on page 12
        When the person opens documents
        Then the row shows «Не удалось»
        And the row shows that page 12 could not be read
        """
        signed_in_browser.given_a_signed_in_person_with_a_document_that_failed_on_page_12()
        document_library.when_the_person_opens_documents()
        document_library.then_there_is_one_document_row()
        document_library.then_the_row_shows_failed()
        document_library.then_the_row_shows_that_page_12_could_not_be_read()
