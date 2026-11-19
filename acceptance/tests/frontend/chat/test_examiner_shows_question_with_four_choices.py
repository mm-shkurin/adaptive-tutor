import pytest

from statements.chat_screen_statements import EXAMINER_QUESTION
from tests.frontend.abstract_ui_test import AbstractUiTest


@pytest.mark.frontend
class TestExaminerShowsQuestionWithFourChoices(AbstractUiTest):
    """UI Test Scenario 3.7: Examiner shows one question with four choices and no page

    Given a signed-in person with an askable chat
    When the person chooses Examiner
    Then one question with four choices is shown
    And the page is not shown yet
    """

    def test_should_show_examiner_question_with_four_choices(self, signed_in_browser, chat_screen):
        signed_in_browser.given_a_signed_in_person_with_an_askable_chat()
        signed_in_browser.script_tutor(EXAMINER_QUESTION)
        chat_screen.when_the_person_opens_the_chat()
        chat_screen.when_the_person_chooses_examiner()
        chat_screen.then_one_question_with_four_choices_is_shown_without_a_page(EXAMINER_QUESTION)
