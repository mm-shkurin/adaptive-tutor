import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.backend
class TestOneSendIsStoredAfterTheStoreRecovers(AbstractBackendTest):
    """One send is stored after the store recovers.

    Given the chat store was down and is back
    And a signed-in person with an askable chat
    When the person sends a line
    Then that line is stored once
    """

    def test_should_store_one_line_after_recovery(self, chats):
        chats.given_the_chat_store_was_down_and_is_back()
        chats.when_the_person_sends_a_line_after_recovery()
        chats.then_that_line_is_stored_once()
