import pytest

from tests.frontend.abstract_ui_test import AbstractUiTest


@pytest.mark.frontend
class TestHistoryAndSourcesReachableOnNarrowWindow(AbstractUiTest):
    """UI Test Scenario 1.4: History and sources stay reachable on a narrow window

    Given a signed-in person with a chat that has a tutor line and a source
    When the person opens that chat on a narrow window
    Then the history can be reached
    And the sources can be reached
    """

    def test_should_keep_history_and_sources_reachable(
        self, signed_in_browser, chat_screen
    ):
        signed_in_browser.given_a_signed_in_person_with_a_chat_that_has_a_person_line_and_a_tutor_line()
        chat_screen.when_the_person_opens_the_chat_on_a_narrow_window()
        chat_screen.then_history_and_sources_can_be_reached()
