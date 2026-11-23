import pytest

from statements.quiz_browser_statements import valid_quiz_body
from tests.frontend.abstract_ui_test import AbstractUiTest


@pytest.mark.frontend
class TestSecondPressWhileGeneratingStoresOneQuiz(AbstractUiTest):
    """UI 3.2: A second press while generating stores one quiz."""

    def test_should_store_one_quiz(self, quiz_browser, quiz_screen):
        quiz_browser.given_a_signed_in_person_with_two_ready_pdfs()
        scripted = quiz_browser.quizzes.script_tutor(
            quiz_browser.signed_in.token, valid_quiz_body(5)
        )
        assert scripted.status_code == 204
        quiz_browser.and_the_quiz_tutor_is_held()
        quiz_screen.when_the_person_opens_the_quizzes()
        quiz_screen.when_the_person_opens_create()
        quiz_screen.when_the_person_fills_create("cells", 5)
        quiz_screen.when_the_person_generates_twice_without_waiting()
        quiz_browser.wait_until_quiz_tutor_hold_entered()
        quiz_browser.release_held_quiz_tutor()
        quiz_screen.then_first_question_is_shown()
        quiz_browser.then_one_quiz_is_stored()
