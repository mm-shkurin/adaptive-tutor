import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.backend
class TestContinuingTheExaminerSeriesWithTheSupportedChoice(AbstractBackendTest):
    """Continuing the examiner series with the supported choice.

    Given a signed-in person who has graded fewer than two examiner questions
    And an examiner question is open
    When the person chooses the choice the piece supports
    Then the grade is right
    And the grade shows that piece's starting page
    And the thread gains exactly one new question
    """

    def test_should_grade_right_and_post_the_next_question(self, chats):
        chats.given_a_signed_in_person_who_has_graded_fewer_than_two_examiner_questions()
        chats.and_an_examiner_question_is_open()
        chats.when_the_person_chooses_the_choice_the_piece_supports()
        chats.then_the_grade_is_right_with_the_piece_page_and_one_new_question()
