import pytest

from tests.frontend.abstract_ui_test import AbstractUiTest


@pytest.mark.frontend
class TestPresentationDoorOpensEditor(AbstractUiTest):
    """UI 1.1: Create presentation opens the editor

    Given a signed-in person on documents
    When the person activates «Создать презентацию»
    Then the presentation editor opens with the default title
    And no PDF upload starts
    """

    def test_should_open_the_editor_without_uploading_a_pdf(
        self, signed_in_browser, document_library
    ):
        signed_in_browser.given_a_signed_in_person_with_no_documents()
        document_library.when_the_person_opens_documents()
        document_library.when_the_person_activates_create_presentation()
        document_library.then_the_presentation_editor_is_open()
        document_library.then_the_presentation_editor_is_empty_draft()
        document_library.then_no_pdf_upload_starts()
