import pytest

from tests.frontend.abstract_ui_test import AbstractUiTest


@pytest.mark.frontend
class TestBackDuringQuizLeavesAttemptOpen(AbstractUiTest):
    """UI 6.3: Back to the list during a quiz leaves the attempt open."""

    def test_should_leave_attempt_open(self, quiz_browser, quiz_screen):
        quiz_browser.given_a_signed_in_person_on_an_unanswered_question()
        quiz_screen.when_the_person_opens_the_quizzes()
        quiz_screen.when_the_person_opens_the_card()
        quiz_screen.when_the_person_goes_back_to_the_list()
        quiz_screen.then_list_is_shown()
        opened = quiz_browser.quizzes.get(quiz_browser.signed_in.token, quiz_browser.quiz_id)
        assert opened.status_code == 200
        assert opened.body["status"] == "take"
        assert opened.body["current_index"] == 0
