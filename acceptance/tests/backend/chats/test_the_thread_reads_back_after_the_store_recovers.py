import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.backend
class TestTheThreadReadsBackAfterTheStoreRecovers(AbstractBackendTest):
    """The thread reads back after the store recovers.

    Given the chat store was down and is back
    And a signed-in person with an askable chat
    When the person reads the chat
    Then the thread is the thread from before the outage
    """

    def test_should_restore_the_thread(self, chats):
        chats.given_the_chat_store_was_down_and_is_back()
        chats.when_the_person_reads_the_chat_after_recovery()
        chats.then_the_thread_is_the_thread_from_before_the_outage()
