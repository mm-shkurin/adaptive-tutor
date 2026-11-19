import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.backend
class TestADeadChatStoreRefusesAReadANewChatAndASwitch(AbstractBackendTest):
    """A dead chat store refuses a read, a new chat, and a switch.

    Given a signed-in person
    And the chat store is down
    When the person reads / starts / opens
    Then the call is refused
    And no chat is created
    """

    def test_should_refuse_a_read(self, chats):
        chats.given_a_signed_in_person_who_has_a_chat()
        chats.and_the_chat_store_is_down()
        chats.when_the_person_reads_a_chat_while_store_down()
        chats.then_the_call_is_refused_and_no_chat_is_created()

    def test_should_refuse_a_new_chat(self, chats):
        chats.given_a_signed_in_person_who_has_a_chat()
        chats.and_the_chat_store_is_down()
        chats.when_the_person_starts_a_chat_while_store_down()
        chats.then_the_call_is_refused_and_no_chat_is_created()

    def test_should_refuse_a_switch(self, chats):
        chats.given_a_signed_in_person_who_has_a_chat()
        chats.and_the_chat_store_is_down()
        chats.when_the_person_opens_a_chat_for_a_document_while_store_down()
        chats.then_the_call_is_refused_and_no_chat_is_created()
