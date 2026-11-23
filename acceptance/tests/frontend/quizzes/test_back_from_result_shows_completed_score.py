import pytest

from tests.frontend.abstract_ui_test import AbstractUiTest


@pytest.mark.frontend
class TestBackFromResultShowsCompletedScore(AbstractUiTest):
    """UI 6.6: Back to the list from the result shows the completed score."""

    def test_should_show_completed_score_on_card(self, quiz_browser, quiz_screen):
        quiz_browser.given_a_signed_in_person_with_a_finished_quiz()
        quiz_screen.when_the_person_opens_the_quizzes()
        quiz_screen.when_the_person_opens_the_card()
        quiz_screen.then_result_shows_score_and_review()
        quiz_screen.when_the_person_goes_back_to_the_list()
        quiz_screen.then_card_keeps_previous_score()
