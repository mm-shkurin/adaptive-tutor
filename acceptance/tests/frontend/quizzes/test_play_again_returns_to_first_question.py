import pytest

from tests.frontend.abstract_ui_test import AbstractUiTest


@pytest.mark.frontend
class TestPlayAgainReturnsToFirstQuestion(AbstractUiTest):
    """UI 5.2: Play again returns to the first question and the card keeps the previous score."""

    def test_should_replay_and_keep_score_on_card(self, quiz_browser, quiz_screen):
        quiz_browser.given_a_signed_in_person_with_a_finished_quiz()
        quiz_screen.when_the_person_opens_the_quizzes()
        quiz_screen.when_the_person_opens_the_card()
        quiz_screen.when_the_person_plays_again()
        quiz_screen.then_first_question_is_shown()
        quiz_screen.when_the_person_goes_back_to_the_list()
        quiz_screen.then_card_keeps_previous_score()
