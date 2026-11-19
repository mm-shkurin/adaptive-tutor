import pytest

from statements.chat_screen_statements import RELEASE, SOCRATIC_QUESTION
from tests.frontend.abstract_ui_test import AbstractUiTest


@pytest.mark.frontend
class TestTryShowsAnswerWithPage(AbstractUiTest):
    """UI Test Scenario 3.5: A try shows the answer with a page

    Given a signed-in person whose tutor is withholding
    When the person sends a try
    Then the tutor shows the answer with a page
    """

    def test_should_show_answer_with_page_after_try(self, signed_in_browser, chat_screen):
        signed_in_browser.given_a_signed_in_person_whose_tutor_is_withholding()
        signed_in_browser.script_tutor(RELEASE)
        chat_screen.when_the_person_opens_the_chat()
        chat_screen.when_the_person_sends_a_try()
        chat_screen.then_the_tutor_shows_the_answer_with_a_page(
            RELEASE,
            signed_in_browser.page,
        )
