import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.backend
class TestChatReplyUnderPeakBurstStaysInsideLatencyBudget(AbstractBackendTest):
    """Load Test Scenario 1.1: A chat reply under the peak burst stays inside the latency budget

    Given the chat latency baseline
    And each person has an askable chat
    When the peak burst sends
    Then each reply arrives whole
    And the replies stay inside the chat latency budget
    And a failed fake is counted as a failed reply, not as a hung send
    """

    def test_should_keep_peak_burst_replies_inside_the_latency_budget(self, chats):
        chats.given_the_chat_latency_baseline()
        chats.and_each_person_has_an_askable_chat()
        chats.when_the_peak_burst_sends()
        chats.then_each_reply_arrives_whole()
        chats.then_the_replies_stay_inside_the_chat_latency_budget()
        chats.then_a_failed_fake_is_counted_as_a_failed_reply_not_as_a_hung_send()
