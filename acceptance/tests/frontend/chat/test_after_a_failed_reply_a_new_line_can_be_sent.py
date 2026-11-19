import pytest

from statements.chat_screen_statements import PERSON_QUESTION, TUTOR_ANSWER
from tests.frontend.abstract_ui_test import AbstractUiTest


@pytest.mark.frontend
class TestAfterAFailedReplyANewLineCanBeSent(AbstractUiTest):
    """UI Test Scenario 3.12: After a failed reply a new line can be sent

    Given a signed-in person whose reply failed
    When the person sends a new line
    Then that line is shown
    """

    def test_should_show_the_new_line_after_a_failed_reply(
        self, signed_in_browser, chat_screen
    ):
        """Given a signed-in person whose reply failed
        When the person sends a new line
        Then that line is shown
        """
        signed_in_browser.given_a_signed_in_person_whose_reply_will_fail()
        chat_screen.when_the_person_opens_the_chat()
        chat_screen.when_the_person_sends_a_question_that_fails(PERSON_QUESTION)
        signed_in_browser.script_tutor(TUTOR_ANSWER)
        new_line = "А что про определитель?"
        chat_screen.when_the_person_sends_a_question(new_line)
        chat_screen.then_the_new_person_line_is_shown(new_line)
