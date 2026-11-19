import pytest

from statements.chat_screen_statements import EXAMINER_QUESTION
from tests.frontend.abstract_ui_test import AbstractUiTest


@pytest.mark.frontend
class TestChoiceShowsRightOrWrongWithPage(AbstractUiTest):
    """UI Test Scenario 3.8: A choice shows right or wrong with the page

    Given a signed-in person with an open examiner question
    When the person chooses a choice
    Then right or wrong is shown with the page
    """

    def test_should_show_grade_with_page_after_choice(self, signed_in_browser, chat_screen):
        signed_in_browser.given_a_signed_in_person_with_an_open_examiner_question()
        chat_screen.when_the_person_opens_the_chat()
        chat_screen.when_the_person_chooses_a_choice("c1")
        chat_screen.then_right_or_wrong_is_shown_with_the_page(signed_in_browser.page)
