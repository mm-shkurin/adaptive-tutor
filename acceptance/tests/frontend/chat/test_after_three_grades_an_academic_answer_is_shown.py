import pytest

from tests.frontend.abstract_ui_test import AbstractUiTest


@pytest.mark.frontend
class TestAfterThreeGradesAnAcademicAnswerIsShown(AbstractUiTest):
    """UI Test Scenario 3.9: After three grades an academic answer is shown

    Given a signed-in person whose examiner series has three grades
    When the person sends a line
    Then an academic answer with a page is shown
    And the quiz list does not contain those questions
    """

    def test_should_show_academic_answer_and_leave_quizzes_empty(
        self, signed_in_browser, chat_screen
    ):
        """Given a signed-in person whose examiner series has three grades
        When the person sends a line
        Then an academic answer with a page is shown
        And the quiz list does not contain those questions
        """
        signed_in_browser.given_a_signed_in_person_whose_examiner_series_has_three_grades()
        chat_screen.when_the_person_opens_the_chat()
        chat_screen.when_the_person_sends_a_question()
        chat_screen.then_an_academic_answer_with_a_page_is_shown(
            signed_in_browser.tutor_line, signed_in_browser.page
        )
        chat_screen.then_the_quiz_list_does_not_contain_those_questions(
            signed_in_browser.examiner_question_texts
        )
