import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.backend
class TestADeadChatStoreRefusesTheSendAndStoresNoLine(AbstractBackendTest):
    """A dead chat store refuses the send and stores no line.

    Given a signed-in person with an askable chat
    And the chat store is down
    When the person sends a line
    Then the send is refused
    And no line is stored
    """

    def test_should_refuse_the_send(self, chats):
        chats.given_a_signed_in_person_who_has_a_chat()
        chats.and_the_chat_store_is_down()
        chats.when_the_person_sends_a_line_while_store_down()
        chats.then_the_send_is_refused_and_no_line_is_stored()
