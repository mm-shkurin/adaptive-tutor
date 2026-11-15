import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.backend
class TestPersonWithNoReadyPdfCannotStartAChat(AbstractBackendTest):
    """A person with no ready PDF cannot start a chat.

    Given a signed-in person with no ready PDF
    When the person starts a chat
    Then the start is refused
    And the chat list is empty
    """

    def test_should_refuse_start_when_no_ready_pdf(self, chats):
        chats.given_a_signed_in_person_with_no_ready_pdf()
        chats.when_the_person_starts_a_chat()
        chats.then_the_start_is_refused()
        chats.then_the_chat_list_is_empty()
