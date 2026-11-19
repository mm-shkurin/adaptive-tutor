import pytest

from tests.frontend.abstract_ui_test import AbstractUiTest


@pytest.mark.frontend
class TestLastModelAndModeStayOnThisDevice(AbstractUiTest):
    """UI Test Scenario 2.4: The last model and the last mode stay on this device

    Given a signed-in person who chose a model and a mode
    When the person opens the chat again on this device
    Then that model is still chosen
    And that mode is still chosen
    """

    def test_should_restore_model_and_mode_after_reopen(
        self, signed_in_browser, chat_screen
    ):
        signed_in_browser.given_a_signed_in_person_with_an_askable_chat()
        chat_screen.when_the_person_opens_the_chat()
        chat_screen.when_the_person_chooses_model_and_mode(
            "qwen/qwen3-32b", "socratic"
        )
        chat_screen.when_the_person_leaves_and_opens_the_chat_again()
        chat_screen.then_that_model_and_mode_are_still_chosen(
            "qwen/qwen3-32b", "socratic"
        )
