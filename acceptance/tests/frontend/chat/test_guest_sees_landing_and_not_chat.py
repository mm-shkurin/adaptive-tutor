import pytest

from tests.frontend.abstract_ui_test import AbstractUiTest


@pytest.mark.frontend
class TestGuestSeesLandingAndNotChat(AbstractUiTest):
    """UI Test Scenario 0.1: A guest sees the landing and not the chat

    Given a guest
    When the guest opens the product
    Then the landing is shown
    And the chat list is not shown
    And the composer is not shown
    """

    def test_should_show_landing_without_chat(
        self, signed_in_browser, chat_screen
    ):
        signed_in_browser.given_a_guest()
        chat_screen.when_the_guest_opens_the_product()
        chat_screen.then_the_landing_is_shown()
        chat_screen.then_the_chat_list_is_not_shown()
        chat_screen.then_the_composer_is_not_shown()
