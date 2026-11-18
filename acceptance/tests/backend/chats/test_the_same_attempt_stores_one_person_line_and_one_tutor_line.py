import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.backend
class TestTheSameAttemptStoresOnePersonLineAndOneTutorLine(AbstractBackendTest):
    """The same attempt stores one person line and one tutor line.

    Given a signed-in person with an askable chat
    When the person delivers the same attempt twice
    Then the thread contains one person line and one tutor line
    And the model is called once
    """

    def test_should_replay_the_same_attempt_without_a_second_call(self, chats):
        chats.given_a_signed_in_person_with_an_askable_chat()
        chats.when_the_person_delivers_the_same_attempt_twice()
        chats.then_the_thread_contains_one_person_line_and_one_tutor_line()
        chats.then_the_model_is_called_once()
