import pytest

from tests.frontend.abstract_ui_test import AbstractUiTest


@pytest.mark.frontend
class TestOpeningCardResumesSavedQuestion(AbstractUiTest):
    """UI 6.4: Opening the card resumes the saved question."""

    def test_should_resume_saved_question(self, quiz_browser, quiz_screen):
        quiz_browser.given_a_signed_in_person_mid_quiz_after_one_answer()
        quiz_screen.when_the_person_opens_the_quizzes()
        quiz_screen.when_the_person_opens_the_card()
        quiz_screen.then_question_is_resumed()
        opened = quiz_browser.quizzes.get(quiz_browser.signed_in.token, quiz_browser.quiz_id)
        assert opened.body["current_index"] == 1
