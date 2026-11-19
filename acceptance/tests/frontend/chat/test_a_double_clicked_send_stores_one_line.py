import pytest

from statements.chat_screen_statements import PAGE, PERSON_QUESTION, TUTOR_ANSWER
from tests.frontend.abstract_ui_test import AbstractUiTest


@pytest.mark.frontend
class TestADoubleClickedSendStoresOneLine(AbstractUiTest):
    """UI Test Scenario 3.3: A double-clicked send stores one line

    Given a signed-in person with an askable chat
    When the person activates send twice without waiting
    Then the thread shows one person line and one tutor line
    """

    def test_should_store_one_person_and_one_tutor_line(
        self, signed_in_browser, chat_screen
    ):
        signed_in_browser.given_a_signed_in_person_with_an_askable_chat()
        signed_in_browser.script_tutor(TUTOR_ANSWER)
        chat_screen.when_the_person_opens_the_chat()
        chat_screen.when_the_person_activates_send_twice_without_waiting(PERSON_QUESTION)
        chat_screen.then_the_thread_shows_the_person_line_the_tutor_line_the_model_and_the_page(
            PERSON_QUESTION, TUTOR_ANSWER, "auto", PAGE
        )
        signed_in_browser.then_one_person_and_one_tutor_line_are_stored()
