import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.backend
class TestAFailedModelCallKeepsOnePersonLine(AbstractBackendTest):
    """A failed model call keeps one person line and no tutor line.

    Given a signed-in person with an askable chat
    And the model call fails
    When the person sends a line
    Then the thread has one person line
    And the thread has no tutor line
    When the person repeats that same attempt
    Then the thread still has one person line
    """

    @pytest.mark.parametrize(
        "how",
        [
            "times out",
            "returns a 4xx status",
            "returns a 5xx status",
            "returns a malformed body",
        ],
    )
    def test_should_keep_one_person_line(self, chats, how):
        chats.given_a_signed_in_person_with_an_askable_chat()
        chats.and_the_model_call_fails(how)
        chats.when_the_person_sends_a_line_expecting_failure()
        chats.then_the_thread_has_one_person_line()
        chats.then_the_thread_has_no_tutor_line()
        chats.when_the_person_repeats_that_same_attempt()
        chats.then_the_thread_has_one_person_line()
