import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.backend
class TestSwitchingDocumentKeepsPreviousChat(AbstractBackendTest):
    """Switching document keeps the previous chat and opens the chosen PDF.

    Scenario Outline:
    Given a signed-in person with a chat that already has a person line
    When the person switches to <chosen>
    Then the previous chat still has that person line
    And the opened chat is <opened>
    """

    def test_should_open_the_newest_chat_for_a_pdf_that_already_has_one(self, chats):
        """Given a signed-in person with a chat that already has a person line
        When the person switches to a ready PDF that already has a chat
        Then the previous chat still has that person line
        And the opened chat is the newest chat for that PDF
        """
        chats.given_a_signed_in_person_with_a_chat_that_already_has_a_person_line()
        chats.when_the_person_switches_to_a_ready_pdf_that_already_has_a_chat()
        chats.then_the_previous_chat_still_has_that_person_line()
        chats.then_the_opened_chat_is_the_newest_chat_for_that_pdf()

    def test_should_create_an_empty_chat_for_a_pdf_with_no_chat(self, chats):
        """Given a signed-in person with a chat that already has a person line
        When the person switches to a ready PDF with no chat
        Then the previous chat still has that person line
        And the opened chat is a new empty chat for that PDF
        """
        chats.given_a_signed_in_person_with_a_chat_that_already_has_a_person_line()
        chats.when_the_person_switches_to_a_ready_pdf_with_no_chat()
        chats.then_the_previous_chat_still_has_that_person_line()
        chats.then_the_opened_chat_is_a_new_empty_chat_for_that_pdf()
