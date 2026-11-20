import pytest

from statements.signed_in_browser_statements import READY_NAME, SECOND_NAME
from tests.frontend.abstract_ui_test import AbstractUiTest

DRAFT = "черновик вопроса без отправки"


@pytest.mark.frontend
class TestUnsentTextStaysInComposerAfterLeaveAndReturn(AbstractUiTest):
    """UI Test Scenario 2.6: Unsent text is still in the composer after leaving and returning

    Given a signed-in person who has typed a line and not sent it
    When the person switches documents and returns to that chat
    Then the unsent line is still in the composer
    """

    def test_should_keep_unsent_composer_text(
        self, signed_in_browser, chat_screen
    ):
        signed_in_browser.given_a_signed_in_person_with_two_ready_pdfs_and_an_askable_chat()
        chat_screen.when_the_person_opens_the_chat()
        chat_screen.when_the_person_types_an_unsent_line(DRAFT)
        chat_screen.when_the_person_switches_to_another_ready_pdf(SECOND_NAME)
        chat_screen.when_the_person_returns_to_the_left_chat(READY_NAME)
        chat_screen.then_the_unsent_line_is_still_in_the_composer(DRAFT)
