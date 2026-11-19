import pytest

from tests.frontend.abstract_ui_test import AbstractUiTest


@pytest.mark.frontend
class TestALaterResponseIsNotReplacedByTheEarlierOne(AbstractUiTest):
    """UI Test Scenario 3.15: A later response that arrives first is not replaced by the earlier one

    Given a signed-in person with two sends still in flight on the open chat
    When the later response arrives before the earlier one
    Then the thread shows the later response
    And the earlier response does not remove it
    """

    def test_should_keep_later_response_when_earlier_arrives_after(
        self, signed_in_browser, chat_screen
    ):
        signed_in_browser.given_a_signed_in_person_with_an_askable_chat()
        signed_in_browser.and_two_ordered_tutor_replies_are_held()
        chat_screen.when_the_person_opens_the_chat()
        chat_screen.when_the_person_sends_without_waiting_for_the_reply(
            signed_in_browser.earlier_question
        )
        signed_in_browser.wait_until_tutor_holds_entered(1)
        chat_screen.when_the_person_sends_without_waiting_for_the_reply(
            signed_in_browser.later_question
        )
        signed_in_browser.wait_until_tutor_holds_entered(2)
        signed_in_browser.release_tutor_call(1)
        chat_screen.then_the_tutor_shows_text(signed_in_browser.later_answer)
        signed_in_browser.release_tutor_call(0)
        chat_screen.then_the_thread_shows_the_later_response_and_keeps_it(
            signed_in_browser.later_answer,
            signed_in_browser.earlier_answer,
        )
