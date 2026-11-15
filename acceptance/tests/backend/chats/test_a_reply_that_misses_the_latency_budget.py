import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.backend
class TestAReplyThatMissesTheLatencyBudget(AbstractBackendTest):
    """A reply that misses the latency budget keeps one person line and no tutor line.

    Given a signed-in person with an askable chat
    When the reply does not finish within the chat latency budget
    Then the thread has one person line
    And the thread has no tutor line
    And the reply work does not continue after the budget
    """

    def test_should_keep_person_line_and_stop_work(self, chats):
        chats.given_a_signed_in_person_with_an_askable_chat()
        chats.when_the_reply_does_not_finish_within_the_chat_latency_budget()
        chats.then_the_thread_has_one_person_line()
        chats.then_the_thread_has_no_tutor_line()
        chats.then_the_reply_work_does_not_continue_after_the_budget()
