import pytest

from tests.frontend.abstract_ui_test import AbstractUiTest


@pytest.mark.frontend
class TestUnansweredQuestionHidesPage(AbstractUiTest):
    """UI 1.3: An unanswered question hides the page and does not offer skip."""

    def test_should_hide_page_and_skip(self, quiz_browser, quiz_screen):
        quiz_browser.given_a_signed_in_person_on_an_unanswered_question()
        quiz_screen.when_the_person_opens_the_quizzes()
        quiz_screen.when_the_person_opens_the_card()
        quiz_screen.then_four_choices_hide_page_and_skip()
