import pytest

from statements.signed_in_browser_statements import SECOND_NAME
from tests.frontend.abstract_ui_test import AbstractUiTest


@pytest.mark.frontend
class TestALateReplyIsNotPaintedOnTheChatNowShown(AbstractUiTest):
    """UI Test Scenario 3.13: A late reply is not painted on the chat now shown

    Given a signed-in person who sent a line and then switched documents
    When the reply for the chat they left arrives
    Then that reply is not painted on the chat now shown
    """

    def test_should_ignore_late_reply_after_document_switch(
        self, signed_in_browser, chat_screen
    ):
        signed_in_browser.given_a_signed_in_person_with_two_ready_pdfs_and_an_askable_chat()
        signed_in_browser.and_the_tutor_reply_is_held()
        chat_screen.when_the_person_opens_the_chat()
        chat_screen.when_the_person_sends_while_the_reply_is_held()
        chat_screen.when_the_person_switches_to_another_ready_pdf(SECOND_NAME)
        signed_in_browser.release_held_tutor()
        signed_in_browser.then_the_left_chat_stored_the_tutor_reply()
        chat_screen.then_that_reply_is_not_painted_on_the_chat_now_shown(
            signed_in_browser.tutor_line
        )
