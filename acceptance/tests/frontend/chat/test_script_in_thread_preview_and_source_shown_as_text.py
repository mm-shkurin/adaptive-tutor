import pytest

from tests.frontend.abstract_ui_test import AbstractUiTest

SCRIPT = "<script>alert(1)</script>"


@pytest.mark.frontend
class TestScriptInThreadPreviewAndSourceShownAsText(AbstractUiTest):
    """UI Test Scenario 1.5: A script in the thread, the preview, and the source is shown as text

    Given a signed-in person
    And a person line, a tutor line, a list preview, and a source that each contain a script
    When the person opens that chat
    Then each of those texts is shown as text
    And none of them is a script element
    """

    def test_should_render_script_payload_as_text(
        self, signed_in_browser, chat_screen
    ):
        signed_in_browser.given_a_signed_in_person_with_script_texts_in_thread_preview_and_source(
            SCRIPT
        )
        chat_screen.when_the_person_opens_the_chat()
        chat_screen.then_script_texts_are_shown_as_text_not_elements(SCRIPT)
