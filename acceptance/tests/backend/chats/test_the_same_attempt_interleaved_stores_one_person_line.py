import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.backend
class TestTheSameAttemptInterleavedStoresOnePersonLine(AbstractBackendTest):
    """The same attempt interleaved stores one person line.

    Given a signed-in person with an askable chat
    When two deliveries of the same attempt interleave between the read of that attempt and the write
    Then the thread contains one person line and one tutor line
    And the model is called once
    """

    def test_should_store_one_person_line_and_call_the_model_once(self, chats):
        chats.given_a_signed_in_person_with_an_askable_chat()
        chats.when_two_deliveries_of_the_same_attempt_interleave_between_the_read_of_that_attempt_and_the_write()
        chats.then_the_interleaved_thread_contains_one_person_line_and_one_tutor_line()
        chats.then_the_model_is_called_once()
