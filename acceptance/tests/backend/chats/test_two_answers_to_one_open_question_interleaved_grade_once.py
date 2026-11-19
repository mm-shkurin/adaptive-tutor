import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.backend
class TestTwoAnswersToOneOpenQuestionInterleavedGradeOnce(AbstractBackendTest):
    """Two answers to one open question interleaved grade once.

    Given a signed-in person with an open examiner question
    When two choices interleave between the read of the question and the write
    Then the thread has one grade
    """

    def test_should_grade_once(self, chats):
        chats.given_a_signed_in_person_with_an_open_examiner_question()
        chats.when_two_choices_interleave_between_the_read_of_the_question_and_the_write()
        chats.then_the_thread_has_one_grade()
