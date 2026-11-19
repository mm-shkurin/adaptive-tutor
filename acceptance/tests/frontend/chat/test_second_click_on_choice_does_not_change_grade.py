import pytest

from statements.chat_screen_statements import EXAMINER_QUESTION
from tests.frontend.abstract_ui_test import AbstractUiTest


@pytest.mark.frontend
class TestSecondClickOnChoiceDoesNotChangeGrade(AbstractUiTest):
    """UI Test Scenario 3.10: A second click on the same choice does not change the grade

    Given a signed-in person whose examiner question is already graded
    When the person chooses again
    Then the grade is unchanged
    """

    def test_should_keep_grade_unchanged_on_second_choice(self, signed_in_browser, chat_screen):
        signed_in_browser.given_a_signed_in_person_whose_examiner_question_is_already_graded()
        chat_screen.when_the_person_opens_the_chat()
        before = chat_screen.grade_labels()
        chat_screen.when_the_person_chooses_again()
        assert chat_screen.grade_labels() == before
