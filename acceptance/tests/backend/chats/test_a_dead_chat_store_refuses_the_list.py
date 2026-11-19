import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.backend
class TestADeadChatStoreRefusesTheList(AbstractBackendTest):
    """A dead chat store refuses the list.

    Given a signed-in person who has a chat
    And the chat store is down
    When the person reads the chat list
    Then the read is refused
    And no chat is returned
    """

    def test_should_refuse_the_list(self, chats):
        chats.given_a_signed_in_person_who_has_a_chat()
        chats.and_the_chat_store_is_down()
        chats.when_the_person_reads_the_chat_list_while_store_down()
        chats.then_the_list_read_is_refused_and_no_chat_is_returned()
