import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.backend
class TestTwoStaleCopiesOfAGradeDoNotDoubleIt(AbstractBackendTest):
    """Two stale copies of a grade do not double it.

    Given a signed-in person with an open examiner question
    And two stale copies of that question
    When each copy saves a different choice
    Then the thread has one grade
    And the second save does not add another grade
    """

    def test_should_keep_one_grade(self, chats):
        chats.given_a_signed_in_person_with_an_open_examiner_question()
        chats.given_two_stale_copies_of_that_question()
        chats.when_each_copy_saves_a_different_choice()
        chats.then_the_thread_has_one_grade_and_the_second_save_does_not_add_another()
