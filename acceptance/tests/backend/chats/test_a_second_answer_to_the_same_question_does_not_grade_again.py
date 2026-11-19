import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.backend
class TestASecondAnswerToTheSameQuestionDoesNotGradeAgain(AbstractBackendTest):
    """A second answer to the same question does not grade again.

    Given a signed-in person whose examiner question is already graded
    When the person chooses again
    Then the grade is unchanged
    And the thread has one grade for that question
    """

    def test_should_keep_the_existing_grade(self, chats):
        chats.given_a_signed_in_person_whose_examiner_question_is_already_graded()
        chats.when_the_person_chooses_again()
        chats.then_the_grade_is_unchanged_and_the_thread_has_one_grade_for_that_question()
