import pytest

from tests.frontend.abstract_ui_test import AbstractUiTest


@pytest.mark.frontend
class TestWhileReplyInFlightScreenShowsWorking(AbstractUiTest):
    """UI Test Scenario 3.16: While the reply is in flight the screen shows that it is working

    Given a signed-in person with an askable chat
    When the reply is still in flight
    Then the screen shows that it is working
    And that state is not the failure message
    """

    def test_should_show_working_state_not_failure(
        self, signed_in_browser, chat_screen
    ):
        """Given a signed-in person with an askable chat
        When the reply is still in flight
        Then the screen shows that it is working
        And that state is not the failure message
        """
        signed_in_browser.given_a_signed_in_person_with_an_askable_chat()
        signed_in_browser.and_the_tutor_reply_is_held()
        chat_screen.when_the_person_opens_the_chat()
        chat_screen.when_the_person_sends_while_the_reply_is_held()
        chat_screen.then_the_screen_shows_that_it_is_working_and_not_the_failure_message()
        signed_in_browser.release_held_tutor()
