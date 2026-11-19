import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.backend
class TestTwoDifferentAttemptsInFlightBothRemain(AbstractBackendTest):
    """Two different attempts in flight both remain in the thread.

    Given a signed-in person with an askable chat
    When two different attempts interleave between the read of the thread and the write
    Then both person lines remain in the thread
    And neither replaces the other
    """

    def test_should_keep_both_person_lines(self, chats):
        chats.given_a_signed_in_person_with_an_askable_chat()
        chats.when_two_different_attempts_interleave_between_the_read_of_the_thread_and_the_write()
        chats.then_both_person_lines_remain_in_the_thread()
        chats.and_neither_replaces_the_other()
