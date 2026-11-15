import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.backend
class TestAFailedReplyKeepsOnePersonLine(AbstractBackendTest):
    """A failed reply keeps one person line for that attempt.

    Given a signed-in person with an askable chat
    And the reply fails after the vectors are ready
    When the person repeats that same attempt
    Then the thread has one person line
    And the thread has no tutor line
    """

    def test_should_keep_one_person_line_and_no_tutor_line(self, chats):
        chats.given_a_signed_in_person_with_an_askable_chat()
        chats.and_the_reply_fails_after_the_vectors_are_ready()
        chats.when_the_person_repeats_that_same_attempt()
        chats.then_the_thread_has_one_person_line()
        chats.then_the_thread_has_no_tutor_line()
