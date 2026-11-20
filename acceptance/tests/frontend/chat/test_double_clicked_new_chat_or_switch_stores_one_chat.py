import pytest

from statements.signed_in_browser_statements import READY_NAME, SECOND_NAME
from tests.frontend.abstract_ui_test import AbstractUiTest


@pytest.mark.frontend
class TestDoubleClickedNewChatOrSwitchStoresOneChat(AbstractUiTest):
    """UI Test Scenario 2.5: A double-clicked new chat or switch stores one chat

    Scenario Outline:
    Given a signed-in person with a selected ready PDF
    When the person activates <control> twice without waiting
    Then one chat effect is stored
    """

    def test_should_store_one_new_chat(self, signed_in_browser, chat_screen):
        signed_in_browser.given_a_signed_in_person_with_an_askable_chat()
        chat_screen.when_the_person_opens_the_chat()
        before = signed_in_browser.chat_count()
        chat_screen.when_the_person_activates_new_chat_twice_without_waiting()
        signed_in_browser.then_one_new_chat_effect_is_stored(before)

    def test_should_store_one_switch_effect(self, signed_in_browser, chat_screen):
        signed_in_browser.given_a_signed_in_person_with_two_ready_pdfs_and_an_askable_chat()
        chat_screen.when_the_person_opens_the_chat()
        chat_screen.when_the_person_activates_switch_document_twice_without_waiting(
            SECOND_NAME
        )
        signed_in_browser.then_one_switch_effect_is_stored(SECOND_NAME)
        signed_in_browser.then_one_switch_effect_is_stored(READY_NAME)
