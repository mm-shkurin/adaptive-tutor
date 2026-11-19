import pytest

from tests.frontend.abstract_ui_test import AbstractUiTest


@pytest.mark.frontend
class TestNoReadyPdfShowsEmptyState(AbstractUiTest):
    """UI Test Scenario 0.2: No ready PDF shows an empty state and send adds nothing

    Given a signed-in person with no ready PDF
    When the person opens the chat
    Then the empty state is shown
    And sending adds no line
    """

    def test_should_show_empty_state_and_refuse_send(
        self, signed_in_browser, chat_screen
    ):
        signed_in_browser.given_a_signed_in_person_with_no_documents()
        chat_screen.when_the_person_opens_the_chat()
        chat_screen.then_the_empty_state_is_shown()
        chat_screen.when_the_person_tries_to_send_from_empty_state()
        chat_screen.then_sending_added_no_line()
