import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest

VALUES = (
    "a null model",
    "a null mode",
    "a model that is not in the list",
    "a mode that is not in the list",
    "an empty model",
    "an empty mode",
)


@pytest.mark.backend
class TestAnUnknownOrNullModelOrModeIsRefused(AbstractBackendTest):
    """An unknown or null model or mode is refused and nothing is stored.

    Scenario Outline:
    Given a signed-in person with an askable chat
    When the person sends a line with <value>
    Then the send is refused
    And the thread is unchanged
    """

    @pytest.mark.parametrize("value", VALUES)
    def test_should_refuse_the_send_and_leave_the_thread(self, chats, value):
        chats.given_a_signed_in_person_with_an_askable_chat()
        chats.when_the_person_sends_a_line_with_value(value)
        chats.then_the_send_is_refused_for_model_or_mode()
        chats.then_the_thread_is_unchanged_after_refused_send()
