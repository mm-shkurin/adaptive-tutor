import pytest

from statements.chat_screen_statements import PERSON_QUESTION
from tests.frontend.abstract_ui_test import AbstractUiTest


@pytest.mark.frontend
class TestAFailedReplyIsShownOnTheChat(AbstractUiTest):
    """UI Test Scenario 3.11: A failed reply is shown on the chat

    Given a signed-in person whose reply failed
    When the person looks at the chat
    Then the person's line is shown
    And no tutor line is shown
    And the failure message is shown
    And the screen is not left spinning
    """

    def test_should_show_person_line_failure_and_not_spin(
        self, signed_in_browser, chat_screen
    ):
        """Given a signed-in person whose reply failed
        When the person looks at the chat
        Then the person's line is shown
        And no tutor line is shown
        And the failure message is shown
        And the screen is not left spinning
        """
        signed_in_browser.given_a_signed_in_person_whose_reply_will_fail()
        chat_screen.when_the_person_opens_the_chat()
        chat_screen.when_the_person_sends_a_question_that_fails(PERSON_QUESTION)
        chat_screen.then_the_persons_line_is_shown_without_a_tutor_line(PERSON_QUESTION)
        chat_screen.then_the_failure_message_is_shown(signed_in_browser.failure_message)
        chat_screen.then_the_screen_is_not_left_spinning()
