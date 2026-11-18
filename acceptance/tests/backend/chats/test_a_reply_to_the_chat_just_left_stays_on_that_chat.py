import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.backend
class TestAReplyToTheChatJustLeftStaysOnThatChat(AbstractBackendTest):
    """A reply to the chat just left stays on that chat.

    Given a signed-in person who sent a line to one chat
    When the person switches to another chat before that reply is stored
    Then the reply is stored on the chat that was sent
    And the chat now open does not gain that reply
    """

    def test_should_keep_the_late_reply_on_the_chat_that_was_sent(self, chats):
        chats.given_a_signed_in_person_who_sent_a_line_to_one_chat()
        chats.when_the_person_switches_to_another_chat_before_that_reply_is_stored()
        chats.then_the_reply_is_stored_on_the_chat_that_was_sent()
        chats.then_the_chat_now_open_does_not_gain_that_reply()
