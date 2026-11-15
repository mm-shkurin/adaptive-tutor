import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest

CASES = (
    (
        "just before the chat latency budget expires",
        "then_the_tutor_line_is_kept",
    ),
    (
        "at the instant the chat latency budget expires",
        "then_the_thread_has_one_person_line_and_no_tutor_line_and_the_reply_work_stops",
    ),
    (
        "just after the chat latency budget expires",
        "then_the_thread_has_one_person_line_and_no_tutor_line_and_the_reply_work_stops",
    ),
)


@pytest.mark.backend
class TestTheLatencyBudgetIsPinned(AbstractBackendTest):
    """The latency budget is pinned just before, at, and just after expiry.

    Given a signed-in person with an askable chat
    And the clock is fixed <when>
    When the person sends a line
    Then <outcome>
    """

    @pytest.mark.parametrize("when,then_step", CASES)
    def test_should_pin_the_budget_edge(self, chats, when, then_step):
        chats.given_a_signed_in_person_with_an_askable_chat()
        chats.and_the_clock_is_fixed(when)
        chats.when_the_person_sends_a_line()
        getattr(chats, then_step)()
