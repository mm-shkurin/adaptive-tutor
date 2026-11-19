import pytest

from tests.backend.abstract_backend_test import AbstractBackendTest


@pytest.mark.backend
class TestAfterTheThirdGradeTheNextLineIsAcademic(AbstractBackendTest):
    """After the third grade the next line is academic and is not a quiz.

    Given a signed-in person whose examiner series has three grades
    When the person sends a line
    Then no fourth question appears
    And the tutor answers in an academic tone with a page
    And the quiz list does not contain the three questions
    """

    def test_should_answer_academically_without_a_fourth_question(self, chats):
        chats.given_a_signed_in_person_whose_examiner_series_has_three_grades()
        chats.when_the_person_sends_a_line_after_examiner_series()
        chats.then_no_fourth_question_and_academic_answer_with_page()
        chats.then_the_quiz_list_does_not_contain_the_three_questions()
