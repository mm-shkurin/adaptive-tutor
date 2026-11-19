import pytest

from tests.frontend.abstract_ui_test import AbstractUiTest


@pytest.mark.frontend
class TestABlankLineLeavesTheThreadUnchanged(AbstractUiTest):
    """UI Test Scenario 3.2: A blank line leaves the thread unchanged

    Given a signed-in person with an askable chat
    When the person sends a blank line
    Then the thread is unchanged
    """

    def test_should_refuse_blank_and_keep_thread_empty(
        self, signed_in_browser, chat_screen
    ):
        signed_in_browser.given_a_signed_in_person_with_an_askable_chat()
        chat_screen.when_the_person_opens_the_chat()
        chat_screen.when_the_person_sends_a_blank_line()
        chat_screen.then_the_thread_is_empty()
        chat_screen.then_a_blank_line_refusal_is_shown()
