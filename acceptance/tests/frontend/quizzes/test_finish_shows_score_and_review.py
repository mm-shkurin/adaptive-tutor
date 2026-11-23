import pytest

from tests.frontend.abstract_ui_test import AbstractUiTest


@pytest.mark.frontend
class TestFinishShowsScoreAndReview(AbstractUiTest):
    """UI 5.1: Finish shows the score and the review."""

    def test_should_show_score_and_review(self, quiz_browser, quiz_screen):
        quiz_browser.given_a_signed_in_person_with_a_finished_quiz()
        quiz_screen.when_the_person_opens_the_quizzes()
        quiz_screen.when_the_person_opens_the_card()
        quiz_screen.then_result_shows_score_and_review()
