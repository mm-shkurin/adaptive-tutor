import pytest

from tests.frontend.abstract_ui_test import AbstractUiTest


@pytest.mark.frontend
class TestChoiceShowsRightOrWrong(AbstractUiTest):
    """UI 2.1: A choice shows right or wrong and reveals the page."""

    def test_should_show_grade_and_page(self, quiz_browser, quiz_screen):
        quiz_browser.given_a_signed_in_person_on_an_unanswered_question()
        quiz_screen.when_the_person_opens_the_quizzes()
        quiz_screen.when_the_person_opens_the_card()
        quiz_screen.when_the_person_chooses_choice(0)
        quiz_screen.then_choice_shows_grade_and_page()
