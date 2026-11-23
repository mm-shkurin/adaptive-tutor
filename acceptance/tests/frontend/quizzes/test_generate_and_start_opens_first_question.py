import pytest

from statements.quiz_browser_statements import valid_quiz_body
from tests.frontend.abstract_ui_test import AbstractUiTest


@pytest.mark.frontend
class TestGenerateAndStartOpensFirstQuestion(AbstractUiTest):
    """UI 3.1: Generate and start locks the control and opens the first question."""

    def test_should_open_the_first_question(self, quiz_browser, quiz_screen):
        quiz_browser.given_a_signed_in_person_with_two_ready_pdfs()
        scripted = quiz_browser.quizzes.script_tutor(
            quiz_browser.signed_in.token, valid_quiz_body(5)
        )
        assert scripted.status_code == 204
        quiz_screen.when_the_person_opens_the_quizzes()
        quiz_screen.when_the_person_opens_create()
        quiz_screen.when_the_person_fills_create("cells", 5)
        quiz_screen.when_the_person_generates()
        quiz_screen.then_first_question_is_shown()
