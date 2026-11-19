import pytest

from statements.chat_screen_statements import SOCRATIC_QUESTION
from tests.frontend.abstract_ui_test import AbstractUiTest


@pytest.mark.frontend
class TestSocraticShowsQuestionWithoutPage(AbstractUiTest):
    """UI Test Scenario 3.4: Socratic shows a question without a page

    Given a signed-in person with an askable chat
    When the person sends a question in Socratic mode
    Then the tutor shows a question without a page
    """

    def test_should_show_socratic_question_without_page(self, signed_in_browser, chat_screen):
        signed_in_browser.given_a_signed_in_person_with_an_askable_chat()
        signed_in_browser.script_tutor(SOCRATIC_QUESTION)
        chat_screen.when_the_person_opens_the_chat()
        chat_screen.when_the_person_sends_a_question_in_socratic_mode()
        chat_screen.then_the_tutor_shows_a_question_without_a_page(SOCRATIC_QUESTION)
