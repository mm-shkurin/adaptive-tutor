import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.backend
class TestBlankLineIsRefusedAndNothingIsStored(AbstractBackendTest):
    """A blank line is refused and nothing is stored.

    Scenario Outline:
    Given a signed-in person with an askable chat
    When the person sends <line>
    Then the send is refused
    And the thread is unchanged
    """

    def test_should_refuse_an_empty_line(self, chats):
        chats.given_a_signed_in_person_with_an_askable_chat()
        chats.when_the_person_sends_an_empty_line()
        chats.then_the_send_is_refused_as_empty()
        chats.then_the_thread_is_unchanged_after_refused_send()

    def test_should_refuse_a_line_of_only_spaces(self, chats):
        chats.given_a_signed_in_person_with_an_askable_chat()
        chats.when_the_person_sends_a_line_of_only_spaces()
        chats.then_the_send_is_refused_as_empty()
        chats.then_the_thread_is_unchanged_after_refused_send()
