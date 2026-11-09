import pytest

from tests.frontend.abstract_ui_test import AbstractUiTest


@pytest.mark.frontend
class TestPresentationDoorDoesNotUploadAPdf(AbstractUiTest):
    """UI Test Scenario 6.1: The presentation door does not upload a PDF

    Given a signed-in person on documents
    When the person activates «Создать презентацию»
    Then the document list is unchanged
    And no PDF upload starts
    """

    def test_should_leave_the_list_unchanged_and_start_no_upload(
        self, signed_in_browser, document_library
    ):
        """UI Test Scenario 6.1: The presentation door does not upload a PDF

        Given a signed-in person on documents
        When the person activates «Создать презентацию»
        Then the document list is unchanged
        And no PDF upload starts
        """
        signed_in_browser.given_a_signed_in_person_with_no_documents()
        document_library.when_the_person_opens_documents()
        document_library.when_the_person_activates_create_presentation()
        document_library.then_the_document_list_is_unchanged()
        document_library.then_no_pdf_upload_starts()
        document_library.then_the_list_reads_no_materials()
