import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.backend
class TestGradingTheThirdExaminerQuestion(AbstractBackendTest):
    """Grading the third examiner question.

    Given a signed-in person with the third examiner question open
    When the person chooses a choice the piece does not support
    Then the grade is wrong
    And the grade shows that piece's starting page
    And no further question is posted
    """

    def test_should_grade_wrong_and_stop_the_series(self, chats):
        chats.given_a_signed_in_person_with_the_third_examiner_question_open()
        chats.when_the_person_chooses_a_choice_the_piece_does_not_support()
        chats.then_the_grade_is_wrong_with_the_piece_page_and_no_further_question()
