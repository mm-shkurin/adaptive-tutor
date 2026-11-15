import pytest

from tests.frontend.abstract_ui_test import AbstractUiTest


@pytest.mark.frontend
class TestNewChatOpensEmptyThreadOnSelectedPdf(AbstractUiTest):
    """UI Test Scenario 2.1: New chat opens an empty thread on the selected PDF

    Given a signed-in person with a selected ready PDF
    When the person starts a new chat
    Then the thread is empty
    And the chat is bound to the selected PDF
    """

    def test_should_open_empty_thread_on_selected_pdf(self, signed_in_browser, chat_screen):
        """UI Test Scenario 2.1: New chat opens an empty thread on the selected PDF

        Given a signed-in person with a selected ready PDF
        When the person starts a new chat
        Then the thread is empty
        And the chat is bound to the selected PDF
        """
        signed_in_browser.given_a_signed_in_person_with_a_selected_ready_pdf()
        chat_screen.when_the_person_opens_the_chat()
        chat_screen.when_the_person_starts_a_new_chat()
        chat_screen.then_the_thread_is_empty()
        chat_screen.then_the_chat_is_bound_to_the_selected_pdf(
            signed_in_browser.ready_document.body["name"]
        )
